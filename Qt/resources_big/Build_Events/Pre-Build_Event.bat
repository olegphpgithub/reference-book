@echo off

"%~1\bin\rcc.exe" -name BigResource1 "%~dp0..\BigResource1.qrc" -pass 1 -o "%~dp0..\qrc_BigResource1.cpp"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

"%~2\cl.exe" /c "%~dp0..\qrc_BigResource1.cpp" /MP /GS /analyze- /W1 /Zc:wchar_t /Zi /Gm- /Od /WX- /Zc:forScope /Gd /Oy- /FC /EHsc /nologo /Fo:"%~dp0..\qrc_BigResource1.tmp.obj"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

"%~1\bin\rcc.exe" -name BigResource1 "%~dp0..\BigResource1.qrc" -pass 2 -temp "%~dp0..\qrc_BigResource1.tmp.obj" -o "%~dp0..\qrc_BigResource1.obj"

IF NOT '%ERRORLEVEL%'=='0' GOTO failure

EXIT /B 0

:failure
EXIT /B 1

REM /MP /GS /analyze- /W1 /Zc:wchar_t /I"D:\qt\5.14.2.0.m\include" /I"D:\qt\5.14.2.0.m\include\QtWidgets" /I"D:\qt\5.14.2.0.m\include\QtGui" /I"D:\qt\5.14.2.0.m\include\QtCore" /I"D:\qt\5.14.2.0.m\mkspecs\win32-msvc" /I"Debug\moc" /I"Debug\uic" /Zi /Gm- /Od /Fd"Debug\vc141.pdb" /Zc:inline /fp:precise /D "UNICODE" /D "_UNICODE" /D "WIN32" /D "_ENABLE_EXTENDED_ALIGNED_STORAGE" /D "QT_WIDGETS_LIB" /D "QT_GUI_LIB" /D "QT_CORE_LIB" /errorReport:prompt /WX- /Zc:forScope /Gd /Oy- /MTd /FC /Fa"Debug\" /EHsc /nologo /Fo"Debug\" /Fp"Debug\BigResource1.pch" /diagnostics:classic 