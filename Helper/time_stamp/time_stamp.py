import os
import re
import sys
import math
import argparse
import shutil
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
from pprint import pprint


def rename_file(input_file_path):
    file_path = Path(input_file_path)
    if not file_path.is_file():
        raise Exception("File not found")

    datetime_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M")

    pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}'
    if re.search(pattern, file_path.stem):
        new_name = re.sub(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}', datetime_formatted, file_path.stem)
    else:
        new_name = file_path.stem + r'_' + datetime_formatted

    full_path = f"{new_name}{file_path.suffix}"
    full_path = Path(file_path.parent) / full_path

    file_path.rename(full_path)


if __name__ == '__main__':
    try:
        rename_file(sys.argv[1])
    except Exception as ex:
        print(str(ex))
