@echo off
echo ===================================================
echo   AI Code Translator MCP Server
echo ===================================================
echo.
echo Installing required dependencies...
pip install flask flask-cors google-generativeai

echo.
echo Starting MCP server on port 5000...
echo.

REM Set the Gemini API key as an environment variable
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo

REM Start the MCP server
python simple_mcp_server.py

echo.
echo Server stopped.
pause
