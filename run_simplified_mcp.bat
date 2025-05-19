@echo off
echo ===================================================
echo   AI Code Translator MCP Server (Simplified)
echo ===================================================
echo.
echo Setting up Gemini API key and starting MCP server...
echo.
echo IMPORTANT: Keep this window open while using the server!
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Set the Gemini API key as an environment variable
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo

REM Install dependencies if needed
pip install fastapi uvicorn pydantic google-generativeai

REM Run the server
python mcp_server.py --host 127.0.0.1 --port 8000

REM This pause will only be reached if the server crashes
echo.
echo Server has stopped unexpectedly. Press any key to exit...
pause
