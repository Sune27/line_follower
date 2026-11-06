@echo off
chcp 65001 >nul
title KET NOI NGROK DIEU KHIEN XE DO LINE ESP32

echo =====================================================================
echo    🌐 CẦU NỐI NGROK ĐIỀU KHIỂN XE DÒ LINE ESP32 QUA INTERNET
echo =====================================================================
echo.
set /p ESP_IP="Nhập địa chỉ IP của ESP32 (bấm Enter để dùng mặc định 10.174.162.159): "
if "%ESP_IP%"=="" set ESP_IP=10.174.162.159

echo.
echo [*] Đang mở tunnel tới ESP32 tại http://%ESP_IP%:80 ...
echo [*] Đường link điều khiển trực tuyến cố định của bạn:
echo     👉 https://saturday-sarcasm-quarrel.ngrok-free.dev
echo.
echo ---------------------------------------------------------------------

set "NGROK_EXE=C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
if exist "%NGROK_EXE%" (
    "%NGROK_EXE%" http http://%ESP_IP%:80 --domain=saturday-sarcasm-quarrel.ngrok-free.dev --host-header=rewrite
) else (
    ngrok http http://%ESP_IP%:80 --domain=saturday-sarcasm-quarrel.ngrok-free.dev --host-header=rewrite
)

pause
