"%~dp0MakeCert.exe" -r -pe -n "CN=\"Your company\"" -a sha256 -cy end -sky signature -sv company.pvk company.cer -b 04/30/2023 -e 04/30/2026
"%~dp0pvk2pfx.exe" -pvk company.pvk -spc company.cer -pfx company.pfx
