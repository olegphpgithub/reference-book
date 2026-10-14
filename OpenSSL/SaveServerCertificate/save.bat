@ECHO OFF

IF "%~1" == "" GOTO failure

REM Save full s_client output (including errors) to a log file for diagnostics
"%~dp0openssl.exe" s_client -tls1_1 -cipher "ALL:@SECLEVEL=0" -connect %~1:443 -servername %~1 < NUL > %~1.tls1_1.log 2>&1
REM x509 skips non-PEM text and reads the first certificate block
"%~dp0openssl.exe" x509 -text -in %~1.tls1_1.log > %~1.tls1_1.cer 2>NUL

"%~dp0openssl.exe" s_client -tls1_2 -cipher "ALL:@SECLEVEL=0" -connect %~1:443 -servername %~1 < NUL > %~1.tls1_2.log 2>&1
"%~dp0openssl.exe" x509 -text -in %~1.tls1_2.log > %~1.tls1_2.cer 2>NUL

EXIT /B 0

:failure
EXIT /B 1