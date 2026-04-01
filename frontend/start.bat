@echo off
REM Quick start script for GSTSaathi frontend development (Windows)

echo === GSTSaathi Frontend Quick Start ===

REM Check Node.js version
echo Checking Node.js version...
node --version

REM Check npm version
echo Checking npm version...
npm --version

REM Install dependencies
echo Installing dependencies...
npm install

REM Start development server
echo.
echo === Starting Vite development server ===
echo Frontend: http://localhost:5173
echo.
npm run dev

pause
