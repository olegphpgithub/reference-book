@echo off
set DIR1="%~dp0d"
python "%~dp0anonymize_folder.py" %DIR1%
pause
