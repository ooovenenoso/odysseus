@echo off
setlocal
TITLE Update Odysseus Docker Deployment

echo =========================================
echo Updating Odysseus Docker Deployment...
echo =========================================
echo.

cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed or not on PATH.
  goto :fail
)

where docker >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker is not installed or not on PATH.
  goto :fail
)

echo [+] Pulling latest code from GitHub...
git pull --ff-only
if errorlevel 1 goto :fail

echo.
echo [+] Rebuilding and restarting containers...
docker compose up -d --build
if errorlevel 1 goto :fail

echo.
echo [+] Cleaning up old, dangling Docker images...
docker image prune -f
if errorlevel 1 goto :fail

echo.
echo =========================================
echo Update successfully completed!
echo =========================================
pause
exit /b 0

:fail
echo.
echo =========================================
echo Update failed. See the error output above.
echo =========================================
pause
exit /b 1
