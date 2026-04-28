import subprocess
import re
import os
import sys
from pathlib import Path
import zipfile
import hashlib
import traceback
import shutil


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


def is_wanted_file(path):
    for wanted_file in wanted_files:
        if wanted_file.file_name == path.name:
            return True
    return False


def validate_wanted_file(path):
    md5sum = md5_file(path)
    for wanted_file in wanted_files:
        if md5sum == wanted_file.md5_sum:
            return True
    return False


def dismiss_wanted_file(path):
    os.remove(path.absolute())
    if path.parent.is_dir() and not any(path.parent.iterdir()):
        os.rmdir(path.parent)


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
        archive_path = Path(archive)
        if is_wanted_file(archive_path):
            if archive_path.parent.is_dir():
                destination_folder = out_dir / archive_path.parent.name
                destination_folder.mkdir(parents=True, exist_ok=True)
            else:
                destination_folder = out_dir
            shutil.copy(archive, destination_folder.absolute())
            destination_path = destination_folder / archive_path.name
            if not validate_wanted_file(destination_path):
                dismiss_wanted_file(destination_path)
        else:
            with zipfile.ZipFile(archive) as z:
                z.setpassword(password)
                for name in z.namelist():
                    z_file_path = Path(name)
                    if is_wanted_file(z_file_path):
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

                        if not validate_wanted_file(obtained_file_path):
                            dismiss_wanted_file(obtained_file_path)

    except Exception:
        print("Error processing file: \"%s\"" % archive, file=sys.stderr)
        traceback.print_exc()
