@echo off
set FILE1="%~dp0test_in.txt"
set FILE2="%~dp0test_out.txt"
python "%~dp0tabs_to_spaces.py" %FILE1% %FILE2%
pause
