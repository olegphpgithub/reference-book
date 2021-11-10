@ECHO OFF

IF "%~1" == "" GOTO failure

"%~dp0openssl.exe" s_client -tls1_1 -connect %~1:443 -servername %~1 < NUL 2>NUL | "%~dp0openssl.exe" x509 -text > %~1.tls1_1.cer

"%~dp0openssl.exe" s_client -tls1_2 -connect %~1:443 -servername %~1 < NUL 2>NUL | "%~dp0openssl.exe" x509 -text > %~1.tls1_2.cer

EXIT /B 0

:failure
EXIT /B 1