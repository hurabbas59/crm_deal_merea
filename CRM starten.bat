@echo off
cd /d "%~dp0"
echo Starte Grundstueck-Service (Python, Port 5001)...
start "Grundstueck-Service" cmd /k "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "grundstueck_service.py"

echo Starte Webserver (Node, Port 8080)...
start "CRM-Webserver" cmd /k node "serve.js"

timeout /t 2 /nobreak >nul
start "" "http://localhost:8080/"

echo.
echo Beide Server laufen jetzt in eigenen Fenstern.
echo Diese Fenster einfach offen lassen, solange du im CRM arbeitest.
echo Zum Beenden: die beiden Server-Fenster schliessen.
pause
