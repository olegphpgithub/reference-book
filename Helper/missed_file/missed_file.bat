@echo off
set FILE1="%~dp0a.md5"
set FILE2="%~dp0b.md5"
python "%~dp0missed_file.py" %FILE1% %FILE2% -o out.txt
pause
