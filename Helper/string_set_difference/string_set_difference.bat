@echo off

set FILE1="c:\dir space\list.txt"
set FILE2="c:\dir space\test.csv"

python "%~dp0string_set_difference.py" ^
 %FILE1% ^
 %FILE2%
