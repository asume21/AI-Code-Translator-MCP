@echo off
echo ===================================================
echo   AI Code Translator - Complete Ecosystem
echo ===================================================
echo.
echo Starting the complete AI Code Translator ecosystem...
echo.
echo IMPORTANT: Keep this window open while using the application!
echo.

REM Set the required environment variables
set GEMINI_API_KEY=AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo
set JWT_SECRET=your_secret_key_for_jwt_tokens
set STRIPE_API_KEY=sk_test_your_stripe_test_key

REM Create database directory if it doesn't exist
if not exist "D:\Projects\AI_Projects\AI_Translator_MCP_Server\data" mkdir "D:\Projects\AI_Projects\AI_Translator_MCP_Server\data"

REM Install required dependencies
echo Installing required dependencies...
pip install -r "D:\Projects\AI_Projects\AI_Translator_MCP_Server\requirements.txt" --quiet

REM Start the MCP server with user management in a new window
start "AI Code Translator MCP Server" cmd /k "cd /d D:\Projects\AI_Projects\AI_Translator_MCP_Server && python simple_mcp_server.py"

REM Wait for the server to start
echo Waiting for MCP server to start...
timeout /t 5 /nobreak > nul

REM Open the integrated demo page in the default browser
echo Opening integrated demo page...
start "" "D:\Projects\AI_Projects\AI_Translator_MCP_Server\integrated_demo.html"

REM Open the AI Money Maker frontend in the default browser
echo Opening AI Money Maker frontend...
start "" "D:\AI MONEY MAKER\frontend\simple.html"

echo.
echo The complete AI Code Translator ecosystem is now running!
echo - MCP server is running on http://127.0.0.1:5000
echo - Integrated demo page is open in your browser
echo - AI Money Maker frontend is open in your browser
echo.
echo Features available:
echo - User registration and authentication
echo - Code translation with multiple languages
echo - Vulnerability scanning
echo - Translation history tracking
echo - Subscription management
echo.
echo Press any key to stop the application...
pause

REM When the user presses a key, kill the MCP server process
taskkill /f /im python.exe /fi "WINDOWTITLE eq *AI Code Translator MCP Server*" 2>nul
echo Application stopped.
timeout /t 3 > nul
