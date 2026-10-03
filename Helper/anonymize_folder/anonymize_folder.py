#!/usr/bin/env python3
"""Anonymize / restore file names in a folder using NTFS hard links.

Usage:
    python anonymize_folder.py <path_to_folder>

Layout (all next to the given folder, i.e. in its parent directory):
    <name>              - original folder
    <name>_anonymized   - folder with anonymized file names (hard links)
    <name>.json         - mapping "anonymized name -> original relative path"
    <name>_restored     - folder with restored original names (hard links)

Phases:
    1. Anonymize: if <name>.json does NOT exist, hard links with random names
       are created in <name>_anonymized and the JSON mapping is written.
    2. Restore:   if <name>.json already exists, the files from
       <name>_anonymized are hard-linked back under their original names
       (and original sub-folder structure) into <name>_restored.

Notes:
    - Hard links only work within a single volume (NTFS). Since all folders
      are created next to the source folder, this is satisfied automatically.
    - In the restore phase the original folder is not required to exist,
      only its path (name) is used to locate the JSON and anonymized folder.
    - Empty sub-folders are not preserved.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

ANON_SUFFIX = "_anonymized"
RESTORED_SUFFIX = "_restored"
JSON_SUFFIX = ".json"
ANON_NAME_LENGTH = 8  # length of the random part of an anonymized name


def random_name() -> str:
    """Return a random hex string of ANON_NAME_LENGTH characters."""
    return uuid.uuid4().hex[:ANON_NAME_LENGTH]


def collect_files(root: Path):
    """Yield all regular files under root (recursively), skipping symlinks."""
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=False):
        for filename in filenames:
            full_path = Path(dirpath) / filename
            if full_path.is_symlink() or not full_path.is_file():
                continue
            yield full_path


def anonymize(source: Path, anon_dir: Path, json_path: Path) -> int:
    """Phase 1: create anonymized hard links and the JSON mapping."""
    if not source.is_dir():
        raise SystemExit(f"Error: source folder does not exist: {source}")
    if anon_dir.exists():
        raise SystemExit(
            f"Error: folder already exists but JSON mapping is missing: {anon_dir}\n"
            "Remove or rename it and run the script again."
        )

    mapping = {}  # anonymized name -> original relative path (with '/')
    anon_dir.mkdir(parents=True)

    try:
        for file_path in collect_files(source):
            relative = file_path.relative_to(source).as_posix()
            extension = file_path.suffix  # keep extension so files stay usable

            anon_name = random_name() + extension
            while anon_name in mapping:  # regenerate on the rare collision
                anon_name = random_name() + extension

            os.link(file_path, anon_dir / anon_name)
            mapping[anon_name] = relative
    except Exception:
        # Roll back: remove everything created so far, keep no JSON.
        for anon_name in mapping:
            try:
                (anon_dir / anon_name).unlink()
            except OSError:
                pass
        try:
            anon_dir.rmdir()
        except OSError:
            pass
        raise

    data = {"source_name": source.name, "files": mapping}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(mapping)


def restore(anon_dir: Path, restored_dir: Path, json_path: Path) -> tuple:
    """Phase 2: recreate original names in a third folder from the JSON mapping."""
    if not anon_dir.is_dir():
        raise SystemExit(f"Error: anonymized folder does not exist: {anon_dir}")
    if restored_dir.exists() and any(restored_dir.iterdir()):
        raise SystemExit(f"Error: restore folder already exists and is not empty: {restored_dir}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = data["files"]

    restored_dir.mkdir(parents=True, exist_ok=True)
    restored_root = restored_dir.resolve()

    restored_count = 0
    missing = []

    for anon_name, relative in mapping.items():
        source_file = anon_dir / anon_name
        if not source_file.is_file():
            missing.append(anon_name)
            continue

        target = (restored_dir / Path(*relative.split("/"))).resolve()
        # Protect against malformed JSON that tries to escape the target folder.
        if restored_root not in target.parents:
            print(f"Warning: skipping suspicious path in JSON: {relative}", file=sys.stderr)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(source_file, target)
        restored_count += 1

    return restored_count, missing


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonymize file names in a folder via hard links, or restore them."
    )
    parser.add_argument("folder", help="Path to the folder")
    args = parser.parse_args()

    source = Path(os.path.abspath(args.folder))
    if not source.name:
        raise SystemExit("Error: a drive root cannot be used as the folder.")

    parent = source.parent
    anon_dir = parent / (source.name + ANON_SUFFIX)
    restored_dir = parent / (source.name + RESTORED_SUFFIX)
    json_path = parent / (source.name + JSON_SUFFIX)

    try:
        if json_path.exists():
            print(f"Found {json_path.name}: restoring original names...")
            count, missing = restore(anon_dir, restored_dir, json_path)
            print(f"Done. Restored files: {count}")
            print(f"Output folder: {restored_dir}")
            if missing:
                print(f"Warning: {len(missing)} file(s) from JSON were not found in {anon_dir.name}:",
                      file=sys.stderr)
                for name in missing:
                    print(f"  {name}", file=sys.stderr)
        else:
            print(f"{json_path.name} not found: anonymizing file names...")
            count = anonymize(source, anon_dir, json_path)
            print(f"Done. Anonymized files: {count}")
            print(f"Output folder: {anon_dir}")
            print(f"Mapping file:  {json_path}")
    except OSError as e:
        raise SystemExit(
            f"File system error: {e}\n"
            "Hard links require an NTFS volume and all folders on the same drive."
        )


if __name__ == "__main__":
    main()
