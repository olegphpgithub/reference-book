import os
import os.path
import re
import shutil
import tempfile
import pathlib
import argparse
import time

import lxml  # noqa: F401  (kept for parity with original imports)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

# ---------- Configuration ----------

START_URL = "https://dash.ice.ocsops.com/dashboards?page=1&page_size=100&order=-created_at"
TARGET_CSS = "a.table-main-title"

# Selector for the heading blocks whose text we want to collect.
HEADING_CSS = "div.th-title"

# Fixed delay (in seconds) to let JavaScript fully build the page
# before we read the DOM.
PAGE_RENDER_WAIT_SEC = 10

# Output file name for the collected headings (one heading per line).
HEADINGS_FILE_NAME = "headings.txt"

REMOTE_DEBUG_PORT = 9222
REMOTE_DEBUG_HOST = "127.0.0.1"

# Persistent profile directory used in "launch" mode so that cookies
# (e.g. login session) survive between runs.
PROFILE_DIR_NAME = "chrome_profile"


def find_chromium():
    candidates = [
        os.getenv("CHROMIUM_BIN")
    ]
    for chromium_path in candidates:
        if chromium_path and os.path.exists(chromium_path):
            return chromium_path
    raise RuntimeError("Chromium not found")


class EphemeralFolder:
    def __init__(self, _prefix=r'download_'):
        self.temp_path = tempfile.mkdtemp(prefix=_prefix)

    def __del__(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path, ignore_errors=True)


# ---------- Text helpers ----------

_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    return _WS_RE.sub(" ", (text or "")).strip()


def pause(prompt: str = "Press Enter to exit..."):
    """Batch-like 'pause': block until the user presses Enter."""
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        pass


# ---------- Browser factories ----------

def start_chromium(chromedriver_path: str, download_dir: str, profile_dir: str):
    """Start Chromium with remote debugging enabled and a persistent profile.

    The browser is intentionally left running after this function returns so
    that the user can log in manually. We stop the chromedriver service
    instead of calling driver.quit() (which would terminate the browser).
    """
    options = Options()
    options.binary_location = find_chromium()
    options.page_load_strategy = "normal"

    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument(f"--remote-debugging-port={REMOTE_DEBUG_PORT}")
    options.add_argument("--remote-debugging-address=127.0.0.1")

    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
    })
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_experimental_option("perfLoggingPrefs", {
        "enableNetwork": True,
        "enablePage": True,
    })

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Detach from the browser: stop the chromedriver service WITHOUT quitting
    # the browser. The Chromium process keeps running with its debugging port.
    # try:
    #     driver.service.stop()
    # except Exception:
    #     pass

def create_attach_driver(chromedriver_path: str):
    """Attach to an already running Chromium via the remote debugging port."""
    options = Options()
    options.binary_location = find_chromium()
    options.add_experimental_option("debuggerAddress", f"{REMOTE_DEBUG_HOST}:{REMOTE_DEBUG_PORT}")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


# ---------- Work routine (attach mode only) ----------

def wait_for_js_render(seconds: int = PAGE_RENDER_WAIT_SEC):
    """Fixed delay to let page-side JavaScript finish building the DOM."""
    print(f"    Waiting {seconds}s for JS render...")
    time.sleep(seconds)


def collect_headings(driver):
    """Return a list of heading strings from all matching HEADING_CSS blocks.

    All nested markup is skipped; only the visible text content is kept.
    """
    headings = []
    elements = driver.find_elements(By.CSS_SELECTOR, HEADING_CSS)
    for el in elements:
        try:
            # textContent includes text from nested tags (e.g. <span>),
            # ignoring intermediate elements as requested.
            raw = el.get_attribute("textContent")
            if raw is None:
                raw = el.text or ""
        except StaleElementReferenceException:
            continue
        text = normalize_text(raw)
        if text:
            headings.append(text)
    return headings


def do_work(driver, output_dir: str):
    current_url = driver.current_url or ""
    if current_url.split("#")[0].split("?")[0].rstrip("/") != START_URL.rstrip("/"):
        print(f"Navigating to {START_URL}")
        driver.get(START_URL)
    else:
        print(f"Already on target page: {current_url}")

    wait_for_js_render()

    elements = driver.find_elements(By.CSS_SELECTOR, TARGET_CSS)
    targets = []
    for el in elements:
        try:
            href = el.get_attribute("href")
        except StaleElementReferenceException:
            continue
        if href:
            targets.append(href)

    print(f"Found links: {len(targets)}")

    # Each entry is (page_url, [heading, heading, ...]).
    # The start page goes first, then every linked page in discovery order.
    results = []

    start_headings = collect_headings(driver)
    print(f"[start] {START_URL} -> {len(start_headings)} headings")
    results.append((START_URL, start_headings))

    for idx, href in enumerate(targets, 1):
        print(f"[{idx}/{len(targets)}] {href}")
        try:
            driver.get(href)
            wait_for_js_render()
            page_headings = collect_headings(driver)
            print(f"    Headings: {len(page_headings)}")
            results.append((href, page_headings))
        except WebDriverException as ex:
            print(f"    Error: {ex}")
            continue

    out_path = os.path.join(output_dir, HEADINGS_FILE_NAME)
    with open(out_path, "w", encoding="utf-8") as f:
        for page_url, headings in results:
            f.write(page_url + "\n")
            for h in headings:
                f.write("    " + h + "\n")

    total = sum(len(h) for _, h in results)
    print(f"Saved {total} headings from {len(results)} pages to: {out_path}")


# ---------- CLI ----------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Redash page enumerator.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--launch",
        action="store_true",
        help="Only start Chromium (with remote debugging) and pause. "
             "Use it for the first run, then log in manually in the browser.",
    )
    group.add_argument(
        "--attach",
        action="store_true",
        help="Connect to the already running Chromium and do the actual work.",
    )
    return parser.parse_args()


# ---------- Main ----------

def main():
    args = parse_args()

    current_path = pathlib.Path(__file__).parent.absolute()
    chromedriver_path = os.path.join(current_path, "chromedriver.exe")

    ephemeral_folder = EphemeralFolder()
    download_dir = ephemeral_folder.temp_path

    profile_dir = os.path.join(str(current_path), PROFILE_DIR_NAME)

    if args.launch:
        print("Mode: launch")
        print(f"Starting Chromium with profile: {profile_dir}")
        print(f"Remote debugging: {REMOTE_DEBUG_HOST}:{REMOTE_DEBUG_PORT}")
        start_chromium(chromedriver_path, download_dir, profile_dir)
        print("Chromium started.")
        print("Log in manually, then run again with --attach.")
        pause()
        return

    if args.attach:
        print("Mode: attach")
        print(f"Attaching to Chromium at {REMOTE_DEBUG_HOST}:{REMOTE_DEBUG_PORT}")
        output_dir = os.path.join(str(current_path), "pages")
        os.makedirs(output_dir, exist_ok=True)

        driver = create_attach_driver(chromedriver_path)
        try:
            do_work(driver, output_dir)
        finally:
            print("Done. Browser left running.")
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(str(ex))