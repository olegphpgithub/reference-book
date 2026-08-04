@echo off

set FILE1=c:\list.txt
set FILE2=c:\test.csv

python "%~dp0string_set_difference.py" %FILE1% %FILE2%
