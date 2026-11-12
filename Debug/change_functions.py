import os
import re
import enum
import glob
import argparse
from os import listdir
from pathlib import Path
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
            regex = re.compile(pattern_key, re.IGNORECASE | re.MULTILINE)
            file_data = regex.sub(pattern_value, file_data)
        return file_data


class RightKey(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'//#define RIGHT_KEY', br'#define RIGHT_KEY'),
        ])

        self.patterns_disorganize = dict([
            (br'^#define RIGHT_KEY', br'//#define RIGHT_KEY'),
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


class EliminateCall(Editor):
    # Functions whose calls get replaced with S_OK
    TARGET_FUNCTIONS = (b'DwmGetWindowAttribute', b'DwmSetWindowAttribute')

    # Classifier: the call is replaced only if its 2nd argument is in this list
    TARGET_ATTRIBUTES = [
        b'DWMWA_SYSTEMBACKDROP_TYPE',
    ]

    _CALL_RE = re.compile(
        rb'(?<![\w:])(?:::\s*)?(?:' + b'|'.join(TARGET_FUNCTIONS) + rb')\s*\('
    )
    _ARG_NAME_RE = re.compile(rb'^[&*]?\s*([A-Za-z_]\w*)$')

    @staticmethod
    def _find_call_end(data, open_paren):
        """Return the index right after the ')' matching data[open_paren] == '('."""
        depth = 0
        i = open_paren
        n = len(data)
        while i < n:
            c = data[i:i + 1]
            if c == b'(':
                depth += 1
            elif c == b')':
                depth -= 1
                if depth == 0:
                    return i + 1
            elif c in (b'"', b"'"):  # string / char literal
                quote = c
                i += 1
                while i < n and data[i:i + 1] != quote:
                    if data[i:i + 1] == b'\\':
                        i += 1
                    i += 1
            elif data[i:i + 2] == b'//':  # line comment
                nl = data.find(b'\n', i)
                i = n if nl == -1 else nl
                continue
            elif data[i:i + 2] == b'/*':  # block comment
                end = data.find(b'*/', i + 2)
                i = n if end == -1 else end + 1
            i += 1
        raise ValueError('Unbalanced parentheses in function call')

    @staticmethod
    def _split_args(args_text):
        """Split an argument list on top-level commas."""
        args, depth, cur = [], 0, bytearray()
        for b in args_text:
            ch = bytes([b])
            if ch in (b'(', b'[', b'{'):
                depth += 1
            elif ch in (b')', b']', b'}'):
                depth -= 1
            if ch == b',' and depth == 0:
                args.append(bytes(cur))
                cur = bytearray()
            else:
                cur += ch
        if cur.strip():
            args.append(bytes(cur))
        return [a.strip() for a in args]

    def organize(self, file_data):
        newline = b'\r\n' if b'\r\n' in file_data else b'\n'
        out = bytearray()
        pos = 0

        while True:
            m = self._CALL_RE.search(file_data, pos)
            if not m:
                out += file_data[pos:]
                break

            call_start = m.start()
            open_paren = m.end() - 1
            call_end = self._find_call_end(file_data, open_paren)
            args = self._split_args(file_data[open_paren + 1:call_end - 1])

            # Classifier check: leave the call untouched unless
            # the 2nd argument is one of the known attributes
            if len(args) < 2 or args[1] not in self.TARGET_ATTRIBUTES:
                out += file_data[pos:call_end]
                pos = call_end
                continue

            # Everything before the call on the same line: indent + "return " / "hr = "
            line_start = file_data.rfind(b'\n', 0, call_start) + 1
            prefix = file_data[line_start:call_start]
            indent = prefix[:len(prefix) - len(prefix.lstrip())]
            statement_head = prefix[len(indent):]

            # Collect parameters: plain identifiers (optionally with & or *),
            # skipping constants (ALL_CAPS) and expressions like sizeof(...)
            names = []
            for arg in args:
                am = self._ARG_NAME_RE.match(arg)
                if am:
                    name = am.group(1)
                    if not name.isupper() and name not in names:
                        names.append(name)

            out += file_data[pos:line_start]
            for name in names:
                out += indent + b'UNREFERENCED_PARAMETER(' + name + b');' + newline

            if statement_head.strip():
                out += indent + statement_head + b'S_OK'
                pos = call_end
            else:
                # The call was a standalone statement: drop it together with its ';'
                tail = call_end
                while file_data[tail:tail + 1] in (b' ', b'\t'):
                    tail += 1
                if file_data[tail:tail + 1] == b';':
                    tail += 1
                # Remove the trailing line break too, as the line is gone
                if file_data[tail:tail + 2] == b'\r\n':
                    tail += 2
                elif file_data[tail:tail + 1] == b'\n':
                    tail += 1
                pos = tail

        return bytes(out)


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
            pos = 0
            while True:
                r = regex.search(file_data, pos)
                if r is not None:
                    pos = r.start() + 1
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
                else:
                    break

        return file_data

    def disorganize(self, file_data):
        for pattern_key in self.patterns_disorganize.keys():
            regex = re.compile(pattern_key, re.IGNORECASE)
            pos = 0
            while True:
                r = regex.search(file_data, pos)
                if r is not None:
                    pos = r.start() + 1
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
                else:
                    break

        return file_data


class Miscellaneous(Editor):
    def __init__(self):
        self.patterns_organize = dict([
            (br'(\n\s*)(version\.SendNetVersion\(\);)', br'\g<1>// \g<2>'),
            (br'(rem)\s+(python "%~dp0\.\.\\\.\.\\\.\.\\Tools\\CXR4\\cxr_fake.py" -i "%~dp0\.\.\\CXR\\common_define_strings.cxr")', br'\g<2>'),
            (br'(python "%~dp0\.\.\\\.\.\\\.\.\\Tools\\CXR4\\cxr.py" -i "%~dp0\.\.\\CXR\\common_define_strings.cxr")', br'rem \g<1>')
        ])
        self.patterns_disorganize = dict([
            (br'(\n\s*)// (version\.SendNetVersion\(\);)', br'\g<1>\g<2>'),
            (br'(python "%~dp0\.\.\\\.\.\\\.\.\\Tools\\CXR4\\cxr_fake.py" -i "%~dp0\.\.\\CXR\\common_define_strings.cxr")', br'rem \g<1>'),
            (br'(rem)\s+(python "%~dp0\.\.\\\.\.\\\.\.\\Tools\\CXR4\\cxr.py" -i "%~dp0\.\.\\CXR\\common_define_strings.cxr")', br'\g<2>')
        ])


class WindowsTargetPlatformVersion(Editor):

    @staticmethod
    def find_files(folder: str) -> list[str]:
        root = Path(folder).expanduser().resolve()
        return [str(p) for p in root.rglob("*.vcxproj") if p.is_file()]

    PATTERN = r"<WindowsTargetPlatformVersion>([0-9\.]+)</WindowsTargetPlatformVersion>"
    SUBST = R"<WindowsTargetPlatformVersion>10.0.22000.0</WindowsTargetPlatformVersion>"

    @staticmethod
    def run(folder: str):
        files = WindowsTargetPlatformVersion.find_files(folder)
        for file in files:
            output = None
            with open(file, "r", encoding="utf-8", newline="", errors="surrogateescape") as i:
                data = i.read()
                regex = re.compile(WindowsTargetPlatformVersion.PATTERN, re.IGNORECASE)
                r = regex.search(data)
                if r is not None:
                    version = r.group(1)

                    parts = version.split(".")
                    parts += [None] * (4 - len(parts))
                    major, minor, build, revision = parts[:4]
                    if major == "10":
                        if build is not None:
                            build_list = ["14393", "19041", "20348", "22000", "22621"]
                            if build not in build_list:
                                output = regex.sub(WindowsTargetPlatformVersion.SUBST, data)

            if output is not None:
                with open(file, "w", encoding="utf-8", newline="", errors="surrogateescape") as o:
                    o.write(output)


intent = Intent.organize
# intent = Intent.disorganize

action_dict = list()
action_dict.append(RightKey())
action_dict.append(AddRemoveList())
# action_dict.append(StartUpCheck())
action_dict.append(Miscellaneous())
# action_dict.append(CreateProcess())
action_dict.append(EliminateCall())


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

    extensions = [r'*.cpp', r'*.h', r'*.bat']

    for src_dir in args.source_directory.split(r';'):

        if not os.path.isdir(src_dir):
            print("Source directory \"%s\" does not exist" % src_dir)
            exit(1)

        substitute_recursively(src_dir, extensions)
        WindowsTargetPlatformVersion.run(src_dir)
