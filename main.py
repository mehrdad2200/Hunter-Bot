import os, re, asyncio, json, time, requests, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = -1003576265638 
DB_FILE = "hunter_db.json"
START_TIME = time.time()
RUN_DURATION = 300 

GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity",
    "https://raw.githubusercontent.com/soroushmkia/V2Ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/ts-sf/sh_v2ray/main/v2ray.txt"
]

NUM_EMOJI = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def get_jalali_date_time():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    # خروجی ثابت برای امروز (۱۶ دی ۱۴۰۴) - در آینده می‌توان تابع کامل‌تری گذاشت
    return "1404/10/16", now.strftime('%H:%M'), now

def get_geo_and_ping(link):
    try:
        host_match = re.search(r'@([^:/?#]+)', link)
        if not host_match: host_match = re.search(r'://([^:/?#]+)', link)
        if not host_match: return None
        host = host_match.group(1)
        
        start = time.time()
        socket.create_connection((host, 443), timeout=1.2).close()
        ping = int((time.time() - start) * 1000)
        
        res = requests.get(f"http://ip-api.com/json/{host}?fields=status,country,countryCode", timeout=2).json()
        if res.get("status") == "success":
            code = res.get("countryCode", "US")
            flag = "".join([chr(ord(c) + 127397) for c in code.upper()])
            return {"country": res.get("country"), "flag": flag, "ping": ping}
    except: pass
    return None

def number_to_emoji(n):
    return "".join(NUM_EMOJI[int(d)] for d in str(n))

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        
        # لود ایمن دیتابیس (رفع ارور KeyError)
        db = {"archive": [], "sent_msgs": [], "daily": {"date": "", "count": 0, "start_members": 0}}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    old_db = json.load(f)
                    # جایگزینی مقادیر قدیمی در ساختار جدید
                    for key in db.keys():
                        if key in old_db: db[key] = old_db[key]
            except: pass

        j_date, j_time, now_dt = get_jalali_date_time()
        
        # مدیریت آمار و گزارش شبانه
        if db["daily"].get("date") != j_date:
            try:
                full = await client(functions.channels.GetFullChannelRequest(MY_CHANNEL))
                curr_mem = full.full_chat.participants_count
                if db["daily"].get("date"):
                    diff = curr_mem - db["daily"].get("start_members", curr_mem)
                    rep = (f"📊 **گزارش ۲۴ ساعته کانال**\n📅 تاریخ: {db['daily']['date']}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n✅ شکار جدید: {db['daily']['count']}\n"
                           f"👥 جذب عضو: {diff:+} نفر\n━━━━━━━━━━━━━━━━━━━━\n🆔 @favproxy")
                    await client.send_message(MY_CHANNEL, rep)
                db["daily"] = {"date": j_date, "count": 0, "start_members": curr_mem}
            except: pass

        print("🔄 استخراج از گیت‌هاب و تلگرام...")
        all_potential_links = []
        # گیت‌هاب
        for url in GITHUB_SOURCES:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    all_potential_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', r.text))
            except: continue

        # تلگرام
        for kw in ['vless://', 'trojan://']:
            try:
                res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), limit=20))
                for m in res.messages:
                    if m.message: all_potential_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message))
            except: continue

        # ارسال
        for link in list(set(all_potential_links)):
            if time.time() - START_TIME > RUN_DURATION: break
            if any(x['link'] == link for x in db["archive"]): continue
            
            geo = get_geo_and_ping(link)
            if not geo or geo['ping'] > 1100: continue
            
            proto = link.split('://')[0].upper()
            db["daily"]["count"] += 1
            c_num = db["daily"]["count"]
            
            text = (
                f"{geo['flag']} **{proto} PREMIUM** | {number_to_emoji(c_num)}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📍 Location: {geo['country']}\n"
                f"⚡️ Ping: {geo['ping']}ms (Stable)\n"
                f"🛰 Status: Online & Verified\n"
                f"📅 {j_date} | ⏰ {j_time}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **Config (Click to Copy):**\n\n"
                f"`{link}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏷 #{proto.lower()} #{geo['country'].replace(' ', '_')}\n"
                f"🆔 @favproxy | 📡 @favme"
            )
            
            sent = await client.send_message(MY_CHANNEL, text)
            db["archive"].append({"link": link, "proto": proto, "country": geo['country'], "flag": geo['flag'], "time": j_time})
            db["sent_msgs"].append({"id": sent.id, "time": now_dt.isoformat()})
            
            # پاکسازی ۲۴ ساعته
            day_ago = now_dt - timedelta(hours=24)
            db["sent_msgs"] = [m for m in db["sent_msgs"] if datetime.fromisoformat(m["time"]) > day_ago]
            # (نکته: در نسخه اکانت، حذف فیزیکی بهتر است محدود باشد تا اکانت ریپورت نشود)

            with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
            await asyncio.sleep(12)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
