# ==============================================================================
# WIFI_AP.PY – MODULE TỰ ĐỘNG TÌM VÀ KẾT NỐI WI-FI "Sune" (CHỈ DÙNG STA MODE)
# ==============================================================================
# Đã xóa hoàn toàn chức năng phát Wi-Fi (AP_IF) theo yêu cầu:
#   - Tắt hẳn bộ phát AP_IF để tiết kiệm Pin tối đa cho ESP32.
#   - Tự động quét và kết nối vào mạng Wi-Fi "Sune" (mật khẩu: "mouse_love_rice").
#   - Đèn LED xanh (GPIO 2) chớp khi đang tìm "Sune" và SÁNG ĐỨNG khi đã kết nối.
# ==============================================================================

import network
import time
from machine import Pin
import config


class WiFiStationClient:
    def __init__(self, ssid=None, password=None, timeout_sec=10, led_pin=2):
        self.ssid = ssid or getattr(config, "WIFI_SSID", "Sune")
        self.password = password if password is not None else getattr(config, "WIFI_PASSWORD", "mouse_love_rice")
        self.timeout_sec = timeout_sec

        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

        try:
            self.led = Pin(led_pin, Pin.OUT)
            self.led.value(0)
        except Exception:
            self.led = None

    def _blink(self, count=4, on_ms=70, off_ms=70):
        if not self.led:
            return
        for _ in range(count):
            self.led.value(1)
            time.sleep_ms(on_ms)
            self.led.value(0)
            time.sleep_ms(off_ms)

    def start(self):
        """
        Tắt hoàn toàn AP_IF, sau đó tự động tìm và kết nối vào Wi-Fi 'Sune'.
        """
        # 1. Tắt hẳn chức năng phát Wi-Fi (AP_IF) của ESP32
        try:
            self.ap.active(False)
        except Exception:
            pass

        # 2. Bật chế độ thu Wi-Fi (STA_IF)
        self.sta.active(True)
        time.sleep_ms(200)

        try:
            self.sta.config(txpower=14)
        except Exception:
            pass

        try:
            self.sta.config(dhcp_hostname="xedoline")
        except Exception:
            pass

        print("\n" + "=" * 56)
        print(f" [WIFI] ĐANG TÌM VÀ KẾT NỐI VÀO WI-FI: '{self.ssid}'...")
        print("=" * 56)

        # Thử quét và kết nối tối đa 3 chu kỳ lúc khởi động
        for attempt in range(1, 4):
            target_ssid = self.ssid
            try:
                scan_list = self.sta.scan()
                for item in scan_list:
                    try:
                        found_name = item[0].decode("utf-8").strip()
                        if found_name.lower() == self.ssid.lower():
                            target_ssid = found_name
                            print(f"[WiFi] 📡 Đã tìm thấy sóng '{target_ssid}'!")
                            break
                    except Exception:
                        pass
            except Exception:
                pass

            print(f"[WiFi] ⏳ Đang kết nối tới '{target_ssid}' (Lần {attempt}/3)...")
            try:
                self.sta.disconnect()
            except Exception:
                pass
            time.sleep_ms(100)

            try:
                self.sta.connect(target_ssid, self.password)
            except Exception as e:
                print("[WiFi] Lỗi gọi lệnh connect:", e)

            t0 = time.time()
            while time.time() - t0 < self.timeout_sec:
                if self.sta.isconnected():
                    ip_addr = self.sta.ifconfig()[0]
                    self._blink(5, 60, 60)
                    if self.led:
                        self.led.value(1)

                    print("\n" + "*" * 56)
                    print(f" [WIFI] 🎉 ĐÃ KẾT NỐI THÀNH CÔNG VÀO '{target_ssid}'!")
                    print(f"   👉 Địa chỉ IP điều khiển: http://{ip_addr}")
                    print("   (Mở trình duyệt trên điện thoại và nhập địa chỉ trên)")
                    print("*" * 56 + "\n")
                    return ip_addr

                # Nhấp nháy đèn xanh trong lúc đang chờ kết nối vào Sune
                if self.led:
                    self.led.value(not self.led.value())
                time.sleep_ms(250)

            print(f"[WiFi] ⚠️ Chưa kết nối được '{target_ssid}', đang thử lại...")

        # Nếu chưa bật Hotspot Sune lúc khởi động, để STA tự kết nối ngầm khi bạn bật Sune
        if self.led:
            self.led.value(0)
        try:
            self.sta.connect(self.ssid, self.password)
        except Exception:
            pass
        print(f"[WiFi] ℹ️ Đang chờ bạn bật điểm phát sóng '{self.ssid}'...")
        return "0.0.0.0"

    def check_connection(self):
        """Kiểm tra trạng thái kết nối và cập nhật đèn LED xanh GPIO 2."""
        connected = self.sta.isconnected()
        if self.led:
            self.led.value(1 if connected else 0)
        return connected

    def get_ip(self):
        if self.sta.isconnected():
            return self.sta.ifconfig()[0]
        return "0.0.0.0"


# Giữ bí danh tương thích
WiFiAccessPoint = WiFiStationClient
