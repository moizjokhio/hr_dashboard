@echo off
echo ================================================
echo Starting ODBC File Uploader Server
echo ================================================
echo.
echo Installing required packages...
pip install flask pyxlsb -q
echo.
echo Starting server...
python file_uploader.py
pause
