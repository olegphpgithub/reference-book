import os
import json
import argparse
from collections import OrderedDict


def create_tree(configuration_file_path):
    with open(configuration_file_path, 'r+') as configuration_file_handle:
        json_string = configuration_file_handle.read()
        json_data = json.loads(json_string, object_pairs_hook=OrderedDict)
        path_dict = json_data['paths'][0]
        for path_item in path_dict.values():
            os.makedirs(path_item, exist_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--configuration-file-path', required=True)
    args = parser.parse_args()

    create_tree(args.configuration_file_path)

    pass
