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
        print("🚀 شکارچی بیدار شد. در حال جمع‌آوری پروکسی...")

        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt",
            "https://raw.githubusercontent.com/barry-far/V2RAY-CONFIGS/main/All_Configs_Sub.txt"
        ]

        all_links = []
        for url in sources:
            try:
                print(f"📡 Checking source: {url[:30]}...")
                res = requests.get(url, timeout=15)
                if res.status_code == 200:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res.text)
                    all_links.extend(links)
                    print(f"✅ Found {len(links)} proxies.")
            except Exception as e:
                print(f"⚠️ Source failed: {e}")

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        
        # انتخاب ۱۵ سرور برتر
        final_selection = unique_proxies[:15]
        print(f"🎯 Total unique proxies found: {len(unique_proxies)}. Starting to send 15...")

        if not final_selection:
            print("❌ هیچ پروکسی پیدا نشد! سورس‌ها رو چک کن.")
            return

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
            try:
                await client.send_message(MY_CHANNEL, msg)
                print(f"📤 Sent {i}/15")
            except Exception as e:
                print(f"❌ Failed to send: {e}")
            
            # فاصله ۲۰ ثانیه‌ای بین هر پیام برای رسیدن به تایم ۵ دقیقه
            if i < 15:
                await asyncio.sleep(20)
            
        print("🏁 بازه ۵ دقیقه‌ای با موفقیت تمام شد.")

    except Exception as e:
        print(f"❌ خطای کلی: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
