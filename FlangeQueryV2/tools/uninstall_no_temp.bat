@echo off
setlocal
set "DEST=%LOCALAPPDATA%\Programs\FlangeQuery"
taskkill /IM FlangeQueryV2.exe /F >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$dir=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\法兰管件规格查询';" ^
  "if(Test-Path $dir){Remove-Item $dir -Recurse -Force};" ^
  "$desk=[Environment]::GetFolderPath('Desktop');" ^
  "if($desk){$lnk=Join-Path $desk '法兰管件规格查询.lnk'; if(Test-Path $lnk){Remove-Item $lnk -Force}}"
if exist "%DEST%" rmdir /s /q "%DEST%"
echo 已卸载。
pause
