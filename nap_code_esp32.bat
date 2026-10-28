@echo off
chcp 65001 >nul
title Nap Code Xe Do Line ESP32 (Ket noi Wi-Fi Sune)
cd /d "%~dp0"
echo ============================================================
echo   HE THONG TU DONG NAP CODE XE DO LINE ESP32 (WIFI SUNE)
echo ============================================================
echo.
python firmware\nap_code_esp32.py
echo.
echo ============================================================
echo Hoan tat! Hay xem dia chi IP http://... in o tren (hoac xem
echo trong muc Thiet bi da ket noi cua Hotspot Sune tren ?T).
echo Nhan phim bat ky de dong cua so nay...
pause >nul
