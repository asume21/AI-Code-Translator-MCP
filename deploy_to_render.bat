@echo off
echo ===================================================
echo   AI Code Translator - Deployment to Render.com
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Ask for Gemini API key if not set
if "%GEMINI_API_KEY%"=="" (
    set /p GEMINI_API_KEY="Enter your Gemini API key: "
)

REM Generate a JWT secret if not provided
set JWT_SECRET=
set /p JWT_SECRET="Enter a JWT secret (leave blank to generate one): "
if "%JWT_SECRET%"=="" (
    echo Generating random JWT secret...
    set JWT_SECRET=%RANDOM%%RANDOM%%RANDOM%%RANDOM%
    echo JWT secret generated: %JWT_SECRET%
)

REM Run the deployment script
echo.
echo Running deployment script for Render.com...
python deploy.py --platform render --api-key "%GEMINI_API_KEY%" --jwt-secret "%JWT_SECRET%" --setup-only

echo.
echo Deployment setup completed!
echo Follow the instructions above to complete the deployment to Render.com.
echo.
pause
