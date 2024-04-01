import os
import re
import glob
import argparse
from os import listdir
from collections import OrderedDict

patterns = dict([
                 (br'//#define RIGHT_KEY', br'#define RIGHT_KEY'),
                 # (br'CreateProcess[A,W]\(', br'NULL == __noop('),
                 (br'(\n\s*)(SendProcessList\(\);)', br'\g<1>// \g<2>'),
                 (br'(\n\s*)(SendAddRemoveList\(\);)', br'\g<1>// \g<2>'),
                 (br'(\n\s*)(version\.SendNetVersion\(\);)', br'\g<1>// \g<2>'),
                 (br'(theAppMain\.m_checkCore\.CheckWmi\(\))', br'true'),
                 (br'(\n\s*)(theAppMain\.m_checkCore\.CheckModules\(esetAvastDLLFound\);)', br'\g<1>// \g<2>'),
                 (br'(theAppMain\.m_checkCore\.CheckESET\(.+\);)', br'theAppMain.m_checkCore.m_allChecksStats[eCheckEsetDone] = eCheckPassed;')
])


class Editor:
    def __init__(self):
        self.patterns_organize = dict()
        self.patterns_disorganize = dict()

    def organize(self, file_data):
        for pattern_key in self.patterns_organize.keys():
            pattern_value = self.patterns_organize[pattern_key]
            regex = re.compile(pattern_key, re.IGNORECASE)
            file_data = regex.sub(pattern_value, file_data)
        return file_data

    def disorganize(self, file_data):
        for pattern_key in self.patterns_disorganize.keys():
            pattern_value = self.patterns_disorganize[pattern_key]
            regex = re.compile(pattern_key, re.IGNORECASE)
            file_data = regex.sub(pattern_value, file_data)
        return file_data


class AddRemoveList(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'(\n\s*)(SendProcessList\(\);)', br'\g<1>// \g<2>'),
            (br'(\n\s*)(SendAddRemoveList\(\);)', br'\g<1>// \g<2>'),
        ])

        self.patterns_disorganize = dict([
            (br'(\n\s*)//\s(SendProcessList\(\);)', br'\g<1>\g<2>'),
            (br'(\n\s*)//\s(SendAddRemoveList\(\);)', br'\g<1>\g<2>'),
        ])


action_dict = OrderedDict()
action_dict['market_2940_down'] = AddRemoveList()


def substitute_file(file_name):
    with open(file_name, 'rb') as file:
        file_data = file.read()

    # for pattern_key in patterns.keys():
    #     pattern_value = patterns[pattern_key]
    #     regex = re.compile(pattern_key, re.IGNORECASE)
    #     file_data = regex.sub(pattern_value, file_data)

    for action in action_dict.values():
        file_data = action.organize(file_data)

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