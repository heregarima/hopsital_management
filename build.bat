@echo off
echo ========================================================
echo   Compiling MEDAXIS C++ Web Backend Server
echo ========================================================

g++ -std=c++11 -O2 medaxis_server.cpp -o medaxis_server.exe -lws2_32 -lwsock32

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Binary compiled: medaxis_server.exe
    echo Run using: medaxis_server.exe 8080
) else (
    echo [ERROR] Compilation failed. Ensure MinGW g++ is in your PATH.
)

