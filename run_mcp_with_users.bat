@echo off
echo ===================================================
echo   AI Code Translator MCP Server with User Management
echo ===================================================
echo.
echo Installing required dependencies...
pip install flask flask-cors google-generativeai pyjwt

echo.
echo Setting up environment...
set JWT_SECRET=your-secure-jwt-secret-change-in-production
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo

echo.
echo Starting MCP server on port 5000...
echo.
echo IMPORTANT: Keep this window open while using the application!
echo.

REM Start the MCP server
python simple_mcp_server.py

echo.
echo Server stopped.
pause
