import os
import re
import json
import math
import argparse
import hashlib
import shutil
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from pprint import pprint


class DirectoryPruner:
    def __init__(self):
        self._src_dir = None
        self._ref_file = None
        self._hash_list = []
        pass

    def set_source_directory(self, src_dir):
        self._src_dir = src_dir

    def set_reference_file(self, ref_file):
        self._ref_file = ref_file

    def obtain_hash_list(self):
        pattern = r'\b[0-9A-Fa-f]{32}\b'
        with open(self._ref_file, 'r') as file:
            for line in file:
                matches = re.findall(pattern, line)
                for match in matches:
                    self._hash_list.append(match)

    @staticmethod
    def calculate_md5(self, file_name):
        md5_hash = hashlib.md5()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def prune(self):

        src_files = []
        for f in listdir(self._src_dir):
            file_path = join(self._src_dir, f)
            if isfile(file_path):
                src_files.append(file_path)

        if len(src_files) < 1:
            raise Exception(r'No files found')

        self.obtain_hash_list()

        for file_path in src_files:
            hash_file = self.calculate_md5(self, file_path)
            if hash_file not in self._hash_list:
                os.remove(file_path)
                print("%s - removed" % os.path.basename(file_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-directory', required=True)
    parser.add_argument('--reference-file', required=True)
    args = parser.parse_args()

    dp = DirectoryPruner()
    dp.set_source_directory(args.source_directory)
    dp.set_reference_file(args.reference_file)
    dp.prune()
