@echo off
echo ===================================================
echo   AI Code Translator Simple MCP Server
echo ===================================================
echo.
echo Setting up Gemini API key and starting Simple MCP server...
echo.
echo IMPORTANT: Keep this window open while using the server!
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Set the Gemini API key as an environment variable
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo

REM Install dependencies if needed
pip install flask google-generativeai

REM Run the server
python simple_mcp_server.py

REM This pause will only be reached if the server crashes
echo.
echo Server has stopped unexpectedly. Press any key to exit...
pause
