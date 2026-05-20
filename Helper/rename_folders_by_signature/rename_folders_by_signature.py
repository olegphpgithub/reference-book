from signify.authenticode import AuthenticodeFile
import subprocess
import re
import os
from pathlib import Path
from datetime import datetime


class RenameTask:
    def __init__(self, src_dir_fd, dst_dir_fd):
        self.src = src_dir_fd
        self.dst = dst_dir_fd


rename_task_list = []
root_dir = Path(r"c:\path")

folders = []
files = []

for path in root_dir.rglob("*.exe"):
    if path.is_file():
        if path.parent not in folders:
            folders.append(path.parent)
            files.append(path.absolute())

for file in files:
    path_object = Path(file)

    ca_common_name = r''
    out = subprocess.check_output([
        "powershell",
        "-Command",
        "(Get-AuthenticodeSignature '%s').SignerCertificate.Issuer" % file
    ])

    str12 = out.decode().strip()
    match = re.search(r"CN=(.+)", str12)
    if match:
        ca_common_name = match.group(1)

    beg = ''
    out = subprocess.check_output([
        "powershell",
        "-Command",
        "(Get-AuthenticodeSignature '%s').SignerCertificate.NotBefore" % file
    ])

    beg = out.decode().strip()

    format_datetime = "%Y-%m-%d %H:%M:%S"
    beg_dt = datetime.strptime(beg, format_datetime)
    beg_formatted = beg_dt.strftime("%Y-%m-%d_%H-%M-%S")

    new_folder = '%s_%s' % (beg_formatted, path_object.parent.name)

    destination_folder = root_dir / new_folder
    rename_task = RenameTask(path_object.parent, destination_folder)
    rename_task_list.append(rename_task)

    out = subprocess.check_output([
        "powershell",
        "-Command",
        "(Get-AuthenticodeSignature '%s').SignerCertificate.Subject" % file
    ])

    parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', out.decode().strip())

    common_name = ''
    OID_state = ''
    L = ''
    S = ''
    C = ''
    O_field = ''
    E = ''
    OID_country = ''
    SERIALNUMBER = ''
    for part in parts:
        match = re.search(r"CN=(.+)", part)
        if match:
            common_name = match.group(1).strip()
        match = re.search(r"OID.1.3.6.1.4.1.311.60.2.1.2=(.+)", part)
        if match:
            OID_state = match.group(1).strip()
        match = re.search(r"OID.1.3.6.1.4.1.311.60.2.1.3=(.+)", part)
        if match:
            OID_country = match.group(1).strip()
        match = re.search(r"L=(.+)", part)
        if match:
            L = match.group(1).strip()
        match = re.search(r"S=(.+)", part)
        if match:
            S = match.group(1).strip()
        match = re.search(r"C=(.+)", part)
        if match:
            C = match.group(1).strip()
        match = re.search(r"O=(.+)", part)
        if match:
            O_field = match.group(1).strip()
        match = re.search(r"SERIALNUMBER=(.+)", part)
        if match:
            SERIALNUMBER = match.group(1).strip()
        match = re.search(r"E=(.+)", part)
        if match:
            E = match.group(1).strip()

for rename_task in rename_task_list:
    print("rename %s -> %s" % (rename_task.src, rename_task.dst))
    os.rename(rename_task.src, rename_task.dst)
