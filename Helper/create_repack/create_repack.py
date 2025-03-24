import os
import re
import json
import math
import argparse
import shutil
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from pprint import pprint


class Unit:
    def __init__(self, p, n, m, e):
        self.prefix = p
        self.number = n
        self.param = m
        self.ext = e


class CloneFile:
    def __init__(self, s, d):
        self.src = s
        self.dst = d


def create_repack(src_dir, dst_dir, cpy_mth, file_qnt):

    if src_dir == dst_dir:
        raise Exception(r'Source and destination directories are the same.')

    src_files = []
    for f in listdir(src_dir):
        if isfile(join(src_dir, f)):
            src_files.append(f)

    if len(src_files) < 1:
        raise Exception(r'No files found')

    src_units = list()

    for src_file in src_files:
        m = re.search(r'(\w+)_(\d+)_([0-9A-Za-z]{32})\.(\w+)', src_file)
        if m is not None:
            src_units.append(Unit(m.group(1), m.group(2), m.group(3), m.group(4)))

    if len(src_units) < 1:
        raise Exception(r'None of the files meet the naming criteria.')

    copy_map = OrderedDict()

    if cpy_mth == r'rotation':
        counter = 1
        while counter < file_qnt + 1:
            for src_unit in src_units:
                src_path = join(src_dir, src_unit.prefix)
                src_path += r'_' + src_unit.number + r'_' + src_unit.param + r'.' + src_unit.ext
                dst_path = join(dst_dir, src_unit.prefix)
                dst_path += r'_' + f'{counter:03}' + r'_' + src_unit.param + r'.' + src_unit.ext
                copy_map[counter] = CloneFile(src_path, dst_path)
                counter = counter + 1
                if counter >= file_qnt + 1:
                    break
    elif cpy_mth == r'together':
        counter = 1
        bunch = math.ceil(file_qnt / len(src_units))
        for src_unit in src_units:
            for i in range(bunch):
                src_path = join(src_dir, src_unit.prefix)
                src_path += r'_' + src_unit.number + r'_' + src_unit.param + r'.' + src_unit.ext
                dst_path = join(dst_dir, src_unit.prefix)
                dst_path += r'_' + f'{counter:03}' + r'_' + src_unit.param + r'.' + src_unit.ext
                copy_map[counter] = CloneFile(src_path, dst_path)
                if counter >= file_qnt:
                    break
                counter = counter + 1
            if counter >= file_qnt:
                break

    for copy_item in copy_map.values():
        print(copy_item.src)
        print(copy_item.dst)
        shutil.copyfile(copy_item.src, copy_item.dst)
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-directory', required=True)
    parser.add_argument('--destination-directory', required=True)
    parser.add_argument('--copy-method', required=True)
    parser.add_argument('--file-quantity', required=True)
    args = parser.parse_args()

    create_repack(args.source_directory, args.destination_directory, args.copy_method, int(args.file_quantity))

    pass
