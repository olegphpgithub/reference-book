import os
import re
import sys
import math
import argparse
import shutil
from os import listdir
from os.path import isfile, join
from pprint import pprint


def transform_file(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="utf-8", newline="", errors="surrogateescape") as i:
        with open(output_file_path, "w", encoding="utf-8", newline="", errors="surrogateescape") as o:
            pos = 0
            while True:
                chunk = i.read(1024)
                if not chunk:
                    break
                output = ""
                for sym in chunk:
                    if sym in ['\r', '\n']:
                        pos = 0
                        output += sym
                        continue
                    if sym == '\t':
                        spaces_count = 4 - pos % 4
                        output += " " * spaces_count
                        pos += spaces_count
                    else:
                        output += sym
                        pos += 1
                o.write(output)


if __name__ == '__main__':

    transform_file(sys.argv[1], sys.argv[2])

