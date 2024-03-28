import os
import re
import glob
import argparse
from os import listdir

patterns = dict([
                 (br'//#define RIGHT_KEY', br'#define RIGHT_KEY'),
                 # (br'CreateProcess[A,W]\(', br'NULL == __noop('),
                 (br'(SendProcessList\(\);)', br'// \g<1>'),
                 (br'(SendAddRemoveList\(\);)', br'// \g<1>'),
                 (br'(version\.SendNetVersion\(\);)', br'// \g<1>')
])


def substitute_file(file_name):
    with open(file_name, 'rb') as file:
        file_data = file.read()

    for pattern_key in patterns.keys():
        pattern_value = patterns[pattern_key]
        regex = re.compile(pattern_key, re.IGNORECASE)
        file_data = regex.sub(pattern_value, file_data)

    with open(file_name, 'wb') as file:
        file.write(file_data)

    print(r'%s - %s' % (file_name, r'processed'))


def substitute_recursively(directory_name, extension_list):
    for extension in extension_list:
        for file_name in glob.glob('%s%s%s' % (directory_name, os.sep, extension)):
            if os.path.isfile(file_name):
                substitute_file(file_name)

    for file_name in listdir(directory_name):
        if os.path.isdir(os.path.join(directory_name, file_name)):
            substitute_recursively(os.path.join(directory_name, file_name), extension_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-directory', required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.source_directory):
        print("Source directory \"%s\" does not exist" % args.source_directory)
        exit(1)

    extensions = [r'*.cpp', r'*.h']

    substitute_recursively(args.source_directory, extensions)