
set ZLIB_W32=C:\Libraries\zlib-1.2.7

set MSSDK=c:\Program Files\Microsoft Platform SDK
set VCToolkitInstallDir=c:\Program Files\Microsoft Visual Studio\VC98

scons VERSION=3.08.0.3 MSTOOLKIT=yes SKIPPLUGINS=all SKIPDOC=all SKIPTESTS=all dist-zip
