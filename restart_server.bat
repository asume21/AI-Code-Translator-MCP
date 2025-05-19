@echo off
echo ===================================================
echo   Restarting AI Code Translator MCP Server
echo ===================================================
echo.

REM Kill any existing server processes
echo Stopping any existing server processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *AI Code Translator MCP Server*" 2>nul
timeout /t 2 /nobreak >nul

REM Set the Gemini API key as an environment variable
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo

echo.
echo Starting MCP server with updated code...
echo.
echo IMPORTANT: Keep this window open while using the server!
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Run the server - without reload to avoid auto-shutdown
start "AI Code Translator MCP Server" cmd /k "python server.py --host 127.0.0.1 --port 8000"

echo.
echo Server has been restarted in a new window.
echo.
timeout /t 3 /nobreak >nul
