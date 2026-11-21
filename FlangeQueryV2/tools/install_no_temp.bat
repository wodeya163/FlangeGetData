@echo off
setlocal
set "SRC=%~dp0FlangeQueryV2"
if not exist "%SRC%\FlangeQueryV2.exe" set "SRC=%~dp0..\FlangeQueryV2"
if not exist "%SRC%\FlangeQueryV2.exe" set "SRC=%~dp0..\FlangeQueryV2"
if not exist "%SRC%\FlangeQueryV2.exe" set "SRC=%~dp0..\dist\FlangeQueryV2"
if not exist "%SRC%\FlangeQueryV2.exe" (
  echo 未找到文件夹版 FlangeQueryV2，请保留 dist\FlangeQueryV2 目录。
  pause
  exit /b 1
)
set "DEST=%LOCALAPPDATA%\Programs\FlangeQuery"
echo 安装到: %DEST%
if exist "%DEST%" (
  choice /m "目标已存在，是否覆盖"
  if errorlevel 2 exit /b 0
)
robocopy "%SRC%" "%DEST%" /E /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 (
  echo 复制失败，错误码 %errorlevel%
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws=New-Object -ComObject WScript.Shell;" ^
  "$exe=Join-Path $env:LOCALAPPDATA 'Programs\FlangeQuery\FlangeQueryV2.exe';" ^
  "$dir=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\法兰管件规格查询';" ^
  "New-Item -ItemType Directory -Force -Path $dir | Out-Null;" ^
  "$lnk=$ws.CreateShortcut((Join-Path $dir '法兰管件规格查询.lnk'));" ^
  "$lnk.TargetPath=$exe; $lnk.WorkingDirectory=Split-Path $exe; $lnk.Save();" ^
  "$desk=[Environment]::GetFolderPath('Desktop');" ^
  "if($desk){$d=$ws.CreateShortcut((Join-Path $desk '法兰管件规格查询.lnk'));$d.TargetPath=$exe;$d.WorkingDirectory=Split-Path $exe;$d.Save()}"
echo.
echo 安装完成。开始菜单/桌面已创建快捷方式。
echo 卸载请运行同目录的“卸载（免临时目录）.bat”。
pause
