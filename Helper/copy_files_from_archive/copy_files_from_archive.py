import subprocess
import re
import os
import sys
from pathlib import Path
import zipfile
import hashlib
import traceback


base_dir = Path(os.path.dirname(__file__))
out_dir = base_dir / r'output'
if not out_dir.exists():
    os.mkdir(out_dir)


def md5_file(_path):
    hash_md5 = hashlib.md5()

    with open(_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def build_wanted_list():
    wanted_database = base_dir / r"wanted.txt"
    with open(wanted_database, "r") as f:
        for line in f:
            line = line.strip()
            pattern = r'^([0-9a-fA-F]{32})\s+(\S+)$'
            m = re.search(pattern, line)
            if m is not None:
                field_md5 = m.group(1)
                field_name = m.group(2)
                wanted_files.append(WantedFile(field_name, field_md5))


class WantedFile:
    def __init__(self, file_name, md5_sum):
        self.file_name = file_name
        self.md5_sum = md5_sum


wanted_files = list()
build_wanted_list()

password = b"secret"

root_dir = Path(r"n:\YuriyToChris")

archives = list()
for path in root_dir.rglob("*.zip"):
    if path.is_file():
        archives.append(str(path.absolute()))

for archive in archives:
    try:
        with zipfile.ZipFile(archive) as z:
            z.setpassword(password)

            for name in z.namelist():
                z_file_path = Path(name)
                for wanted_file in wanted_files:

                    if z_file_path.name == wanted_file.file_name:

                        out = subprocess.check_output([
                            "7z.exe",
                            "x",
                            archive,
                            name,
                            "-p%s" % password.decode(),
                            "-o%s" % out_dir,
                            "-aoa"
                        ])

                        obtained_file_path = out_dir / name

                        md5sum = md5_file(obtained_file_path)

                        if md5sum != wanted_file.md5_sum:
                            os.remove(obtained_file_path)
                            if obtained_file_path.parent.is_dir() and not any(obtained_file_path.parent.iterdir()):
                                os.rmdir(obtained_file_path.parent)
                        else:
                            print("Found: " + md5sum + " " + z_file_path.name)
    except Exception:
        print("Error processing file: \"%s\"" % archive, file=sys.stderr)
        traceback.print_exc()
