@echo off
set DIR1="%~dp0dir"
python make_report.py %DIR1% --view=2 -o "%~dp0result_2.txt"
