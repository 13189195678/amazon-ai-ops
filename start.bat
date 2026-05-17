@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Amazon AI Ops - 领星API代理服务器
echo ========================================
echo.

:: Set Python path
set "PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts;%PATH%"

:: Start Flask server in background
echo [INFO] 启动后端代理服务器...
start /B python proxy_server.py > proxy_log.txt 2>&1

:: Wait for server to start
timeout /t 3 /nobreak >nul

:: Open browser
echo [INFO] 打开浏览器...
start http://127.0.0.1:5000

echo.
echo ========================================
echo   系统已启动！
echo   浏览器已打开到 http://127.0.0.1:5000
echo.
echo   如果页面显示空白，请刷新浏览器
echo   关闭此窗口即可停止服务器
echo ========================================
echo.
pause