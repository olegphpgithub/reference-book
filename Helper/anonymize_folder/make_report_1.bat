@echo off
set DIR1="%~dp0dir"
python make_report.py %DIR1% --view=1 -o "%~dp0result_1.txt"
