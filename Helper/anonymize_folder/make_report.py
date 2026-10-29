
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import posixpath
import sys
from collections import defaultdict


def load_data(filename):
    """Load downloader JSON data."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def group_files(data):
    """Group files by their origin directories."""
    groups = defaultdict(list)

    for item in data.get("files", {}).values():
        origin = item.get("origin", "")

        # Support both Unix and Windows-style paths.
        origin = origin.replace("\\", "/")
        folder = posixpath.dirname(origin) or "."
        filename = posixpath.basename(origin)

        groups[folder].append({
            "filename": filename,
            "hash": item.get("hash", ""),
            "status": item.get("status", ""),
        })

    # Sort filenames alphabetically within each directory.
    for files in groups.values():
        files.sort(key=lambda item: item["filename"].casefold())

    return groups


def format_view_1(files):
    """
    Format: HASH  FILENAME  STATUS

    The status column is right-aligned.
    The filename column is left-aligned.
    """
    max_filename = max(len(item["filename"]) for item in files)
    max_status = max(len(item["status"]) for item in files)

    lines = []

    for item in files:
        filename = item["filename"].ljust(max_filename + 2)
        status = item["status"].rjust(max_status)

        lines.append(
            "    {}  {}{}".format(
                item["hash"],
                filename,
                status,
            )
        )

    return lines


def format_view_2(files):
    """
    Format: STATUS  HASH  FILENAME

    The status column is left-aligned.
    Two spaces follow the longest status.
    """
    max_status = max(len(item["status"]) for item in files)

    lines = []

    for item in files:
        status = item["status"].ljust(max_status + 2)

        lines.append(
            "    {}{}  {}".format(
                status,
                item["hash"],
                item["filename"],
            )
        )

    return lines


def create_report(data, view):
    """Create a report with alphabetically sorted directories."""
    groups = group_files(data)
    report = []

    formatter = format_view_1 if view == 1 else format_view_2

    for folder in sorted(groups, key=str.casefold):
        files = groups[folder]

        report.append("## {}".format(folder))
        report.append("")
        report.extend(formatter(files))
        report.append("")

    return "\n".join(report).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Convert downloader JSON into a text report."
    )

    parser.add_argument(
        "input",
        nargs="?",
        default="downloader_example.json",
        help="Input JSON file (default: downloader_example.json)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output text file (default: report_example_<view>.txt)",
    )

    parser.add_argument(
        "--view",
        type=int,
        choices=(1, 2),
        required=True,
        help="Report format: 1 or 2",
    )

    args = parser.parse_args()

    output = args.output or "report_example_{}.txt".format(args.view)

    try:
        data = load_data(args.input)
        report = create_report(data, args.view)

        with open(output, "w", encoding="utf-8", newline="\n") as file:
            file.write(report)

    except (OSError, json.JSONDecodeError) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1

    print("Report saved to: {}".format(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
