import os
import re
import enum
import glob
import argparse
from os import listdir
from collections import OrderedDict


class Intent(enum.Enum):
    organize = 1
    disorganize = 2


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


class RightKey(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'//#define RIGHT_KEY', br'#define RIGHT_KEY'),
        ])

        self.patterns_disorganize = dict([
            (br'#define RIGHT_KEY', br'//#define RIGHT_KEY'),
        ])


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


class StartUpCheck(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'theAppMain\.m_checkCore\.CheckWmi\(\)',
             br'(strcmp("ae36f891-62d6-45b7-88a1-982dcc29e560", "ae36f891-62d6-45b7-88a1-982dcc29e560") == 0)'),
            (br'(\n\s*)(theAppMain\.m_checkCore\.CheckModules\(esetAvastDLLFound\);)',
             br'\g<1>// \g<2>'),
            (br'(theAppMain\.m_checkCore\.CheckESET\(.+\);)',
             br'theAppMain.m_checkCore.m_allChecksStats[eCheckEsetDone] = eCheckPassed; // e89114f6-002e-4887-aca6-499b8371349e'),
            (br'theAppMain\.m_checkCore\.CheckSniffer\(\)',
             br'(0xfe8fe6db == 0xfe8fe6db)'),
            (br'(\n\s*)(IsInsideVMWareNew\(\))',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(CheckModuleLoadedName\b)',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(GetSystemManufacturer\b)',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(CheckCurrentUser\b)',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(IsQEMU\b)',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(CheckRegistryKey2\b)',
             br'\g<1>// \g<2>'),
            (br'(\n\s*)(BigDllManager::SendPixel\b)',
             br'\g<1>// \g<2>'),
        ])

        self.patterns_disorganize = dict([
            (br'\(strcmp\("ae36f891-62d6-45b7-88a1-982dcc29e560", "ae36f891-62d6-45b7-88a1-982dcc29e560"\) == 0\)',
             br'theAppMain.m_checkCore.CheckWmi()'),
            (br'(\n\s*)//\s(theAppMain\.m_checkCore\.CheckModules\(esetAvastDLLFound\);)',
             br'\g<1>\g<2>'),
            (br'theAppMain.m_checkCore.m_allChecksStats[eCheckEsetDone] = eCheckPassed; // e89114f6-002e-4887-aca6-499b8371349e',
             br'(theAppMain.m_checkCore.CheckESET\(.+\);)'),
            (br'\(0xfe8fe6db == 0xfe8fe6db\)',
             br'theAppMain.m_checkCore.CheckSniffer()'),
            (br'(\n\s*)// (IsInsideVMWareNew\(\))',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (CheckModuleLoadedName\b)',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (GetSystemManufacturer\b)',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (CheckCurrentUser\b)',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (IsQEMU\b)',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (CheckRegistryKey2\b)',
             br'\g<1>\g<2>'),
            (br'(\n\s*)// (BigDllManager::SendPixel\b)',
             br'\g<1>\g<2>'),
        ])


class CreateProcess(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'CreateProcess[A,W]?\(', br'0x2cf0368a')
        ])
        self.patterns_disorganize = dict([
            (br'\(0x2cf0368a == 0x2cf0368a\) \/\*\@', br'')
        ])
        self.comment_beg = br'/*@'
        self.comment_end = br'@*/'

    def organize(self, file_data):
        for pattern_key in self.patterns_organize.keys():
            pattern_value = self.patterns_organize[pattern_key]
            regex = re.compile(pattern_key, re.IGNORECASE)
            r = regex.search(file_data)
            if r is not None:
                for reg in r.regs:

                    if reg[0] > len(self.comment_beg) - 1:
                        comment_position = reg[0] - len(self.comment_beg)
                        if file_data[comment_position:reg[0]] == self.comment_beg:
                            break

                    cease = reg[1]
                    deep = 0
                    while True:

                        if cease >= len(file_data):
                            break

                        character = chr(file_data[cease])
                        if character == '(':
                            deep += 1
                        if character == ')':
                            if deep == 0:
                                break
                            else:
                                deep -= 1
                        cease += 1

                    file_data_tmp = file_data[0:reg[0]]
                    file_data_tmp += br"(%s == %s) %s" % (pattern_value, pattern_value, self.comment_beg)
                    file_data_tmp += file_data[reg[0]:cease + 1]
                    file_data_tmp += self.comment_end
                    file_data_tmp += file_data[cease + 1:]

                    file_data = file_data_tmp

        return file_data

    def disorganize(self, file_data):
        for pattern_key in self.patterns_disorganize.keys():
            regex = re.compile(pattern_key, re.IGNORECASE)
            r = regex.search(file_data)
            if r is not None:
                for reg in r.regs:
                    cease = reg[1]
                    while True:

                        if cease >= len(file_data):
                            break

                        sequence = file_data[cease:cease + 3]
                        if sequence == self.comment_end:
                            break

                        cease += 1

                    file_data_tmp = file_data[0:reg[0]]
                    file_data_tmp += file_data[reg[1]:cease]
                    file_data_tmp += file_data[cease + 3:]

                    file_data = file_data_tmp

        return file_data


class Miscellaneous(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'(\n\s*)(version\.SendNetVersion\(\);)', br'\g<1>// \g<2>')
        ])
        self.patterns_disorganize = dict([
            (br'(\n\s*)// (version\.SendNetVersion\(\);)', br'\g<1>\g<2>')
        ])


intent = Intent.organize
# intent = Intent.disorganize

action_dict = list()
action_dict.append(RightKey())
action_dict.append(AddRemoveList())
action_dict.append(StartUpCheck())
action_dict.append(Miscellaneous())
# action_dict.append(CreateProcess())


def substitute_file(file_name):
    with open(file_name, 'rb') as file:
        file_data = file.read()

    for action in action_dict:
        if intent == Intent.organize:
            file_data = action.organize(file_data)
        elif intent == Intent.disorganize:
            file_data = action.disorganize(file_data)

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
