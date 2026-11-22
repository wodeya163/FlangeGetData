@echo off
cd /d "%~dp0..\FlangeQueryV2"
set TAG=v3.78.4
set ZIP=%~1
if "%ZIP%"=="" set ZIP=%~dp0FlangeQueryV2-3.78.4-folder.zip
echo Uploading %ZIP% to wodeya163/FlangeGetData %TAG% ...
python tools\_upload_asset.py wodeya163/FlangeGetData %TAG% "%ZIP%"
if errorlevel 1 (
  echo.
  echo Upload failed. Make sure python is in PATH and `git auth login` was done.
)
pause
