import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات مهرداد هنتر ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')

# آیدی کانال مهرداد (تایید شده)
MY_CHANNEL = -1003576265638 
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

# دیتابیس لوکیشن برای زیبایی پست‌ها
COUNTRY_MAP = {
    'tr': '🇹🇷 TURKEY', 'us': '🇺🇸 USA', 'de': '🇩🇪 GERMANY',
    'ir': '🇮🇷 IRAN', 'nl': '🇳🇱 NETHERLANDS', 'gb': '🇬🇧 UK',
    'fr': '🇫🇷 FRANCE', 'fi': '🇫🇮 FINLAND', 'sg': '🇸🇬 SINGAPORE',
    'jp': '🇯🇵 JAPAN', 'ca': '🇨🇦 CANADA', 'ae': '🇦🇪 UAE'
}

def get_location(url):
    name_part = url.split('#')[-1].lower() if '#' in url else ''
    for code, info in COUNTRY_MAP.items():
        if code in name_part: return info
    return "🌐 GLOBAL"

async def main():
    # اتصال با سشن تایید شده
    client = TelegramClient(StringSession(STRING_SESSION.strip()), API_ID, API_HASH)
    try:
        print("📡 در حال اتصال به سرور تلگرام...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ خطا: سشن معتبر نیست!")
            return

        print("🚀 شکارچی متصل شد. در حال جمع‌آوری از سورس‌ها...")

        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/barry-far/V2RAY-CONFIGS/main/All_Configs_Sub.txt"
        ]

        all_links = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                all_links.extend(links)
            except: continue

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        
        selection = unique_proxies[:15]
        print(f"✅ تعداد {len(selection)} پروکسی آماده ارسال به کانال است.")

        for i, p in enumerate(selection, 1):
            loc = get_location(p)
            msg = (
                f"{BRAND}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📍 **Server {i}/15:** {loc}\n"
                f"⚡ **Status:** `Active` ✅\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **Config:**\n`{p}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 @favproxy"
            )
            
            try:
                # ارسال مستقیم با آیدی عددی
                await client.send_message(MY_CHANNEL, msg)
                print(f"📤 ارسال موفق {i}/15")
            except Exception as e:
                print(f"❌ خطا در ارسال پیام {i}: {e}")
            
            # ایجاد فاصله ۲۰ ثانیه‌ای برای نگه داشتن اکشن به مدت ۵ دقیقه
            if i < 15:
                await asyncio.sleep(20)
            
        print("🏁 عملیات با موفقیت به پایان رسید.")

    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
