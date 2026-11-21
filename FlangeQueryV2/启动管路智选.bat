@echo off
chcp 65001 >nul
setlocal
title 管路智选 - 源码启动
cd /d "%~dp0"

if not exist "main.py" (
  echo.
  echo [无法启动] 未找到 main.py，请在项目根目录运行本脚本。
  pause
  exit /b 1
)

rem 1) 项目内虚拟环境（推荐）
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import PyQt5" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    set "PYTHON_ARGS="
    goto run
  )
)

rem 2) PATH 中的 python
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import PyQt5" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_EXE=python"
    set "PYTHON_ARGS="
    goto run
  )
)

rem 3) Python Launcher：py -3
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import PyQt5" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3"
    goto run
  )
)

rem 4) python3（少数环境）
where python3 >nul 2>nul
if not errorlevel 1 (
  python3 -c "import PyQt5" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_EXE=python3"
    set "PYTHON_ARGS="
    goto run
  )
)

echo.
echo [无法启动] 未找到可用的 Python + PyQt5 环境。
echo 请先执行：
echo     python -m pip install -r requirements.txt
echo 或创建虚拟环境：
echo     python -m venv .venv
echo     .venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
echo 也可以直接运行发布版：
echo     dist\FlangeQueryV2\FlangeQueryV2.exe
echo.
pause
exit /b 1

:run
"%PYTHON_EXE%" %PYTHON_ARGS% main.py
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo [启动失败] 错误码 %RC%
  pause
)
exit /b %RC%
