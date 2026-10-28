# ==============================================================================
# MAIN.PY – CHƯƠNG TRÌNH CHÍNH XE DÒ LINE TỰ HÀNH ESP32 (KẾT NỐI WI-FI "Sune")
# ==============================================================================

import time
import gc
from machine import Pin
import config
from modules.wifi_ap import WiFiStationClient
from modules.line_sensor import LineFollowerSensor
from modules.motor_driver import MotorDriver
from modules.line_tracker import LineTracker
from modules.web_server import WebControlServer


def main():
    print("\n" + "=" * 56)
    print(" [ESP32] KHỞI ĐỘNG HỆ THỐNG XE DÒ LINE 5 MẮT + TB6612FNG")
    print("=" * 56)

    # Kéo 4 chân động cơ xuống mức 0 (LOW) ngay khi bật nguồn để giữ xe đứng im
    for p in (config.PIN_MOTOR_AIN1, config.PIN_MOTOR_AIN2, config.PIN_MOTOR_BIN1, config.PIN_MOTOR_BIN2):
        try:
            Pin(p, Pin.OUT, value=0)
        except Exception:
            pass

    time.sleep_ms(800)

    # 1. Tự động tìm và kết nối vào Wi-Fi "Sune" (Đã tắt hoàn toàn chức năng phát AP)
    wifi_client = WiFiStationClient(
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASSWORD,
        timeout_sec=config.WIFI_CONNECT_TIMEOUT_SEC,
        led_pin=config.PIN_STATUS_LED,
    )
    active_ip = wifi_client.start()

    # 2. Khởi tạo Driver Động cơ TB6612FNG (PWM 4 chân + Kickstart 95%)
    motor = MotorDriver(
        pin_ain1=config.PIN_MOTOR_AIN1,
        pin_ain2=config.PIN_MOTOR_AIN2,
        pin_bin1=config.PIN_MOTOR_BIN1,
        pin_bin2=config.PIN_MOTOR_BIN2,
        freq=config.MOTOR_PWM_FREQ,
    )
    motor.stop()

    # 3. Khởi tạo Mảng cảm biến dò line TCRT5000 5 mắt (D21, D19, D18, D5, D17)
    line_sensor = LineFollowerSensor(
        s1_pin=config.PIN_LINE_S1,
        s2_pin=config.PIN_LINE_S2,
        s3_pin=config.PIN_LINE_S3,
        s4_pin=config.PIN_LINE_S4,
        s5_pin=config.PIN_LINE_S5,
        active_low=config.SENSOR_ACTIVE_LOW,
    )

    # 4. Khởi tạo Bộ điều khiển Dò Line 5 mắt
    tracker = LineTracker(motor_driver=motor)

    # 5. Khởi tạo Web Server điều khiển qua trình duyệt Điện thoại (Cổng 80)
    web = WebControlServer(
        line_sensor=line_sensor,
        motor=motor,
        tracker=tracker,
        port=80,
    )

    last_pid_tick = time.ticks_ms()
    last_wifi_check = last_pid_tick
    loop_interval_ms = getattr(config, "CONTROL_LOOP_MS", 10)

    print(f"[ESP32] ✅ SẴN SÀNG! Mở trình duyệt Điện thoại tại: http://{active_ip}")

    # ==========================================================================
    # VÒNG LẶP CHÍNH THỜI GIAN THỰC (REAL-TIME NON-BLOCKING LOOP)
    # ==========================================================================
    while True:
        try:
            now = time.ticks_ms()

            # ƯU TIÊN 1: Cập nhật Dò Line đúng chu kỳ 10ms (100Hz)
            if tracker.is_active:
                if time.ticks_diff(now, last_pid_tick) >= loop_interval_ms:
                    last_pid_tick = now
                    raw_sensors = line_sensor.read_all_raw()
                    tracker.update(raw_sensors, now)

            # ƯU TIÊN 2: Lắng nghe thao tác bấm nút trên Điện thoại (Non-blocking)
            web.poll()

            # Kiểm tra trạng thái đèn báo Wi-Fi và dọn bộ nhớ mỗi 5 giây khi xe nghỉ
            if not tracker.is_active and time.ticks_diff(now, last_wifi_check) >= 5000:
                last_wifi_check = now
                wifi_client.check_connection()
                gc.collect()

        except Exception as e:
            print("[Main Loop Error]:", e)

        time.sleep_ms(1)


if __name__ == "__main__":
    main()
