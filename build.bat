@echo off
echo Installing PyInstaller...
py -m pip install pyinstaller
echo Building AutoC v2.0 Executable...
py -m PyInstaller --onefile --noconsole --name "AutoC_v2.0" "main.py"
echo Done! The executable is in the 'dist' folder.
pause
