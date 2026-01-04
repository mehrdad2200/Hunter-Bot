import os, re, asyncio, requests, random
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات مهرداد هنتر ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

def get_location(url):
    name = url.split('#')[-1].lower() if '#' in url else ''
    flags = {'tr': '🇹🇷 TR', 'us': '🇺🇸 US', 'de': '🇩🇪 DE', 'ir': '🇮🇷 IR', 'nl': '🇳🇱 NL'}
    for code, info in flags.items():
        if code in name: return info
    return "🌐 GLOBAL"

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 شکارچی استارت زد...")
        
        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/barry-far/V2RAY-CONFIGS/main/All_Configs_Sub.txt"
        ]
        
        all_links = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                all_links.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res))
            except: continue

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        
        selection = unique_proxies[:15]
        for i, p in enumerate(selection, 1):
            loc = get_location(p)
            msg = f"{BRAND}\n━━━━━━━━━━━━\n📍 **Server {i}/15:** {loc}\n⚡ **Status:** `Active` ✅\n━━━━━━━━━━━━\n🔗 **Config:**\n`{p}`\n━━━━━━━━━━━━\n🆔 @{MY_CHANNEL}"
            await client.send_message(MY_CHANNEL, msg)
            print(f"✅ {i}/15 Sent")
            if i < 15: await asyncio.sleep(20) 
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
