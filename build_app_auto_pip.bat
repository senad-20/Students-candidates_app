@echo off
echo ===========================
echo Vérification des modules requis...
echo ===========================

pip show openpyxl >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo openpyxl non trouvé, installation en cours...
    pip install openpyxl
) ELSE (
    echo openpyxl déjà installé.
)

echo.
echo ===========================
echo Compilation de l'application...
echo ===========================
pyinstaller --noconfirm --onefile --windowed --icon=flag.ico --add-data "flag.ico;." main.py

echo.
echo ===========================
echo Terminé ! Le fichier est dans le dossier dist\main.exe
pause
