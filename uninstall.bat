@echo off
REM MCP PDFTools Uninstaller for Windows
REM Version: 1.0

echo.
echo ================================================================
echo          MCP PDFTools - Windows Uninstallation
echo                     Version 1.0
echo ================================================================
echo.
echo To uninstall mcp_pdftools on Windows:
echo.
echo 1. Deactivate virtual environment (if active):
echo    deactivate
echo.
echo 2. Remove the installation directory:
echo    cd %USERPROFILE%
echo    rmdir /s /q mcp_pdftools
echo.
echo 3. (Optional) Uninstall Python, Docker, Git, Node.js
echo    using Windows Settings -^> Apps if you no longer need them
echo.
echo 4. (Optional) Remove log files:
echo    rmdir /s /q %USERPROFILE%\.mcp_pdftools
echo.
echo ================================================================
echo.
echo WARNING: This will delete all mcp_pdftools files!
echo.
set /p confirm=Are you sure you want to continue? (y/N):
if /i "%confirm%"=="y" goto uninstall
if /i "%confirm%"=="yes" goto uninstall
goto cancel

:uninstall
echo.
echo Uninstalling...
cd %USERPROFILE%
if exist mcp_pdftools\venv (
    echo Removing virtual environment...
    rmdir /s /q mcp_pdftools\venv
)
echo.
echo Virtual environment removed.
echo.
echo To remove the entire installation directory, run:
echo   rmdir /s /q %USERPROFILE%\mcp_pdftools
echo.
goto end

:cancel
echo.
echo Uninstallation cancelled.
echo.

:end
pause
