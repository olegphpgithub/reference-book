import io
import os
import chardet
import tempfile
import shutil
import subprocess

EXCLUDED_ENCODINGS = ['utf-8', 'ascii']
PROJECT_DIR = r'e:\NetNucleusRus\Diary\2025\2025-07\2025-07-04\11-30_CheckList\dir'
TARGET_EXTENSIONS = ['.txt', '.c', '.cpp', '.h', '.hpp']


for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if not any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
            continue
        full_path = os.path.join(root, file)
        try:
            with open(full_path, 'rb') as f:
                f.seek(0, io.SEEK_END)
                file_size = f.tell()
                f.seek(0, io.SEEK_SET)
                raw = f.read(file_size)
                result = chardet.detect(raw)
                encoding = result['encoding']

                if encoding and encoding.lower() not in EXCLUDED_ENCODINGS:
                    print(f'{full_path} — {encoding}')

                    tmp_file_path = tempfile.mktemp()

                    convert_command = rf'iconv.exe -f {encoding} -t ascii//IGNORE "{full_path}"'
                    dev_null = open(os.devnull, 'wb')
                    std_out = open(tmp_file_path, 'wb')
                    result = subprocess.Popen(convert_command, stdout=std_out)
                    result.communicate()
                    result.wait()
                    shutil.copy(tmp_file_path, full_path)

                    if result.returncode != 0:
                        raise Exception(r'Failed to convert the file')
                    else:
                        print(r'The file has been successfully converted')

        except Exception as e:
            print(f'Error {full_path}: {e}')
