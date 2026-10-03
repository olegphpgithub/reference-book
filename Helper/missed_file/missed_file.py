#!/usr/bin/env python3
"""Compare two md5 lists (md5sum format) and print a Markdown report.

File 1 is the full list, file 2 is a subset of it.
Lines of file 1 look like:
    752248031de0e708b34e0e8eb63adff6 *folder/_s0512_0.bin
Only md5 sums are taken from file 2: an entry of file 1 counts as found
if its md5 occurs anywhere in file 2, regardless of file names.
Every entry of file 1 is listed (names come from file 1): found ones are
marked OK, the others MISSED. Entries present only in file 2 are ignored.
The whole report is wrapped in a code block (for Mattermost).
"""
import argparse
import re
import sys
from pathlib import PureWindowsPath

# md5, whitespace, optional '*' (md5sum binary mode), path/file name
LINE_RE = re.compile(r"^\s*([a-fA-F0-9]{32})\s+\*?(.+?)\s*$")
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
OK = "OK"
MISSED = "MISSED"
FENCE = "```"
FENCE_LANG = "java"


def parse_file(file_path):
    """Return a list of unique (md5, path) entries in file order."""
    entries = {}
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = LINE_RE.match(line)
            if m:
                entries.setdefault((m.group(1).lower(), m.group(2)), None)
    return list(entries)


def parse_md5s(file_path):
    """Return the set of all md5 sums found in a file (names are ignored)."""
    md5s = set()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            md5s.update(m.lower() for m in MD5_RE.findall(line))
    return md5s


def find_missed(entries1, md5s2):
    """Return entries of file 1 whose md5 is absent from file 2."""
    return frozenset(e for e in entries1 if e[0] not in md5s2)


def split_path(path):
    """Split a path into (folder, name). The folder is empty for bare names.

    PureWindowsPath understands both / and \\.
    """
    p = PureWindowsPath(path)
    folder = p.parent.as_posix()
    return ("" if folder == "." else folder), p.name


def group_by_folder(entries):
    """Return {folder: [(md5, name, original entry)]} in first-seen order."""
    groups = {}
    for entry in entries:
        md5, path = entry
        folder, name = split_path(path)
        groups.setdefault(folder, []).append((md5, name, entry))
    return groups


def format_groups(groups, missed):
    """Return report lines.

    All lines of a group are built first to find the longest one, then the
    others are padded with spaces so their right edges line up.
    The group without a folder goes first and has no heading.
    """
    lines = []
    # Folderless group goes first, otherwise it would visually attach to the heading above
    for folder in sorted(groups, key=lambda f: f != ""):
        items = groups[folder]
        rows = []  # (line start, status)
        for md5, name, entry in items:
            status = " - " + (MISSED if entry in missed else OK)
            rows.append(("%s  %s" % (md5, name), status))

        width = max(len(head) + len(status) for head, status in rows)

        if folder:
            lines.append("## %s" % folder)
            lines.append("")
        for head, status in rows:
            lines.append(head + " " * (width - len(head) - len(status)) + status)
        lines.append("")
    return lines


def build_report(entries1, missed):
    body = "\n".join(format_groups(group_by_folder(entries1), missed)).rstrip()
    return "%s%s\n%s\n%s\n" % (FENCE, FENCE_LANG, body, FENCE)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two md5 lists and print a Markdown report.")
    parser.add_argument("full", help="file 1: the full list")
    parser.add_argument("subset", help="file 2: a subset of file 1 (only md5 sums are used)")
    parser.add_argument("-o", "--output", help="also save the report to a file")
    args = parser.parse_args()

    entries1 = parse_file(args.full)
    md5s2 = parse_md5s(args.subset)
    missed = find_missed(entries1, md5s2)

    report = build_report(entries1, missed)
    print(report, end="")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)

    # Exit code 1 if anything is missed (handy for scripts)
    sys.exit(1 if missed else 0)


if __name__ == "__main__":
    main()
