@echo off
echo Compilation de l'application .EXE avec PyInstaller...
pyinstaller --noconfirm --onefile --windowed --icon=flag.ico --add-data "flag.ico;." main.py
echo.
echo Terminé ! Le fichier se trouve dans le dossier dist\main.exe
pause
