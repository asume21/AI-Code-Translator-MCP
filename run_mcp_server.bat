@echo off
echo Starting AI Code Translator MCP Server...

REM Set environment variables
set GEMINI_API_KEY=%GEMINI_API_KEY%
if "%GEMINI_API_KEY%"=="" (
    echo ERROR: GEMINI_API_KEY environment variable not set
    echo Please set your Gemini API key using:
    echo set GEMINI_API_KEY=your_api_key_here
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Run the server
echo Starting server...
python mcp_server.py --host 127.0.0.1 --port 8000 --reload

pause
