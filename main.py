import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات سیستمی مهرداد ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛡️"

# دیتابیس ایموجی و کشورها
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
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 شکارچی بیدار شد. شروع بازه ۵ دقیقه‌ای...")

        # جمع‌آوری از منابع
        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt"
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
        
        # انتخاب ۱۵ سرور برتر برای این بازه
        final_selection = unique_proxies[:15]

        # ارسال با فاصله ۲۰ ثانیه (مجموعاً ۵ دقیقه بیداری)
        for i, p in enumerate(final_selection, 1):
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
            print(f"✅ ارسال موفق {i}/15 - در حال انتظار برای ارسال بعدی...")
            
            # فاصله ۲۰ ثانیه‌ای بین هر پیام
            if i < 15: await asyncio.sleep(20)
            
        print("🏁 بازه ۵ دقیقه‌ای تمام شد. ربات به استراحت می‌رود.")

    except Exception as e:
        print(f"❌ خطای عملیاتی: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
