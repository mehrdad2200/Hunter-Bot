import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات مهرداد هنتر ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

# دیتابیس لوکیشن
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
    # اتصال با سشن تایید شده مهرداد
    client = TelegramClient(StringSession(STRING_SESSION.strip()), API_ID, API_HASH)
    try:
        print("📡 در حال اتصال به تلگرام...")
        await client.connect()
        print("🚀 شکارچی وارد شد! شروع عملیات...")

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
                f"🆔 @{MY_CHANNEL}"
            )
            await client.send_message(MY_CHANNEL, msg)
            print(f"✅ ارسال موفق {i}/15")
            
            # فاصله ۲۰ ثانیه‌ای برای پر کردن بازه ۵ دقیقه
            if i < 15:
                await asyncio.sleep(20)
            
        print("🏁 سیکل ۱۵ دقیقه‌ای با موفقیت انجام شد.")

    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
