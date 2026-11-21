@echo off
title MEDAXIS – Hospital Management System
echo ========================================================
echo   + MEDAXIS – Hospital Management System (Admin Portal)
echo   * Tagline: Simplifying Hospital Operations. Connecting Better Care.
echo ========================================================
echo.
echo Launching MEDAXIS REST Server on port 5000...
echo Access in browser: http://localhost:5000
echo.

start http://localhost:5000
"C:\Users\thega\anaconda3\python.exe" server.py
pause

