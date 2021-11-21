@echo off

"%~1\bin\rcc.exe" -name BigResource1 "%~dp0..\BigResource1.qrc" -pass 1 -o "%~dp0..\qrc_BigResource1.cpp"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

"%~2\cl.exe" /c "%~dp0..\qrc_BigResource1.cpp" /Fo:"%~dp0..\qrc_BigResource1.tmp.obj"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

"%~1\bin\rcc.exe" -name BigResource1 "%~dp0..\BigResource1.qrc" -pass 2 -temp "%~dp0..\qrc_BigResource1.tmp.obj" -o "%~dp0..\qrc_BigResource1.obj"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

EXIT /B 0

:failure
EXIT /B 1
