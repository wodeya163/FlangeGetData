@echo off
chcp 65001 >nul
cd /d "E:\AI作品\work\FlangeGetData\FlangeQueryV2"
set "PATH=D:\Program Files\Python313;%PATH%"
set "PYTHONPATH=C:\Users\Administrator\.workbuddy\binaries\python\workspace\pylibs"
set "PYTHONIOENCODING=utf-8"

echo [1/3] 语法检查
"D:\Program Files\Python313\python.exe" -m py_compile flange_drawing.py parts_drawing.py
if errorlevel 1 goto failed

echo [2/3] 单元测试
"D:\Program Files\Python313\python.exe" -m unittest discover -s tests
if errorlevel 1 goto failed

echo [3/3] 构建 3.14.x
"D:\Program Files\Python313\python.exe" tools\build_release.py --clean
if errorlevel 1 goto failed

echo.
echo 构建完成。产物在 dist\ 和 FlangeQueryV2_EXE便携版.zip
pause
exit /b 0

:failed
echo.
echo 构建失败，请查看上面的 traceback。
pause
exit /b 1
