import os
import re
import sys
import json
import math
import argparse
import shutil
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from pprint import pprint


MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")


def parse_file(file_path):
    string_set = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            string_set.update(MD5_RE.findall(line))

    return string_set


if __name__ == '__main__':

    for i, arg in enumerate(sys.argv):
        print(i, repr(arg))

    string_set_1 = parse_file(sys.argv[1])
    string_set_2 = parse_file(sys.argv[2])

    only_in_first = string_set_1 - string_set_2
    only_in_second = string_set_2 - string_set_1

    print("Only in %s:" % sys.argv[1])
    pprint(only_in_first)
    print("Only in %s:" % sys.argv[2])
    pprint(only_in_second)

