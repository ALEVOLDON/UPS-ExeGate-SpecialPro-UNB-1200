@echo off
chcp 65001 >nul
setlocal
title ExeGate SpecialPro UPS Monitor - Установка / Installer
cd /d "%~dp0"

echo ======================================================================
echo    ExeGate SpecialPro UPS Monitor - Мастер установки / Installer     
echo ======================================================================
echo.

set "PY_CMD="
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ОШИБКА / ERROR] Python не обнаружен в вашей системе!
    echo [!] Python is not installed or not added to PATH.
    echo.
    echo Пожалуйста, установите Python 3.10+ с официального сайта:
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    echo ВАЖНО: Во время установки обязательно отметьте галочку:
    echo IMPORTANT: Make sure to check "Add python.exe to PATH"!
    echo.
    pause
    exit /b 1
)

echo [*] Обнаружен Python:
%PY_CMD% --version
echo.

echo [1/2] Установка необходимых библиотек (requirements.txt)...
echo [1/2] Installing dependencies...
%PY_CMD% -m pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ОШИБКА / ERROR] Не удалось установить зависимости.
    echo Проверьте подключение к интернету или права доступа.
    pause
    exit /b 1
)
echo.
echo [+] Библиотеки успешно установлены!
echo.

echo [2/2] Создание ярлыка на Рабочем столе...
echo [2/2] Creating Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo [!] Не удалось автоматически создать ярлык, но программа установлена.
)
echo.
echo ======================================================================
echo   [ГОТОВО / SUCCESS] Установка успешно завершена!
echo   Ярлык "ExeGate UPS Monitor" создан на вашем Рабочем столе.
echo ======================================================================
echo.
set /p LAUNCH="Запустить программу прямо сейчас? / Launch now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    echo [*] Запуск приложения...
    start "" "%~dp0Run_UPS_Monitor.vbs"
)
endlocal
