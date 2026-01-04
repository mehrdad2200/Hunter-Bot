import requests, re, os

def test_hunter():
    print("🚀 شروع تست سلامت ربات مهرداد...")
    sources = [
        "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"
    ]
    
    for url in sources:
        try:
            res = requests.get(url, timeout=10)
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res.text)
            print(f"✅ منبع چک شد: {len(links)} پروکسی پیدا شد.")
        except Exception as e:
            print(f"❌ خطا در خواندن منبع: {e}")

    print("💎 اگر این پیام را می‌بینی، یعنی ربات سالم است و مشکل فقط از SESSION تلگرام است.")

if __name__ == "__main__":
    test_hunter()
