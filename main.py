import os, re, asyncio, json, time, requests, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات سیستمی ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = -1003576265638  # آیدی عددی کانال تو
DB_FILE = "hunter_db.json"
START_TIME = time.time()
RUN_DURATION = 300  # ۵ دقیقه فعالیت در هر بار اجرا

# ایموجی اعداد برای شماره پست
NUM_EMOJI = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def get_jalali_date_time():
    """محاسبه دقیق زمان و تاریخ شمسی و ساعت ایران"""
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    gy, gm, gd = now.year, now.month, now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = gy - 621
    days = (gy - 1) * 365 + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + g_d_m[gm - 1] + gd
    jy_all_days = days - ((jy + 620) * 365 + (jy + 620) // 4 - (jy + 620) // 100 + (jy + 620) // 400)
    if jy_all_days > 286:
        jy += 1; jy_all_days -= 286
    else:
        jy_all_days += 79
    if jy_all_days <= 186:
        jm = 1 + (jy_all_days - 1) // 31
        jd = 1 + (jy_all_days - 1) % 31
    else:
        jm = 7 + (jy_all_days - 187) // 30
        jd = 1 + (jy_all_days - 187) % 30
    return f"{jy}/{jm:02d}/{jd:02d}", now.strftime('%H:%M'), now

def get_geo_and_ping(link):
    """تست آی‌پی، استخراج کشور، پرچم و پینگ واقعی"""
    try:
        host_match = re.search(r'@([^:/?#]+)', link)
        if not host_match: host_match = re.search(r'://([^:/?#]+)', link)
        if not host_match: return None
        
        host = host_match.group(1)
        # تست پینگ TCP
        start = time.time()
        socket.create_connection((host, 443), timeout=1.5).close()
        ping = int((time.time() - start) * 1000)
        
        # دریافت اطلاعات کشور
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
        # لود دیتابیس
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: db = json.load(f)
        else:
            db = {"archive": [], "sent_msgs": [], "daily": {"date": "", "count": 0, "start_members": 0}}

        j_date, j_time, now_dt = get_jalali_date_time()
        
        # گزارش 00:00 و ریست آمار
        if db["daily"]["date"] != j_date:
            try:
                full = await client(functions.channels.GetFullChannelRequest(MY_CHANNEL))
                curr_mem = full.full_chat.participants_count
                if db["daily"]["date"]:
                    diff = curr_mem - db["daily"]["start_members"]
                    msg = (f"📊 **خلاصه عملکرد ۲۴ ساعت گذشته**\n📅 تاریخ: {db['daily']['date']}\n"
                           f"━━━━━━━━━━━━━━━━━━━━\n✅ سرورهای جدید: {db['daily']['count']}\n"
                           f"👥 جذب عضو: {diff:+} نفر\n━━━━━━━━━━━━━━━━━━━━\n🆔 @favproxy")
                    await client.send_message(MY_CHANNEL, msg)
                db["daily"] = {"date": j_date, "count": 0, "start_members": curr_mem}
            except: pass

        print("🔍 شروع جستجوی جهانی...")
        while time.time() - START_TIME < RUN_DURATION:
            for kw in ['vless://', 'trojan://', 'ss://']:
                res = await client(functions.messages.SearchGlobalRequest(
                    q=kw, filter=types.InputMessagesFilterEmpty(),
                    min_date=None, max_date=None, offset_id=0,
                    offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
                ))
                
                for m in res.messages:
                    if not m.message: continue
                    links = re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message)
                    for link in links:
                        if any(x['link'] == link for x in db["archive"]): continue
                        
                        geo = get_geo_and_ping(link)
                        if not geo or geo['ping'] > 1200: continue # فیلتر پینگ بالا
                        
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
                        db["archive"].append({"link": link, "time": now_dt.isoformat()})
                        db["sent_msgs"].append({"id": sent.id, "time": now_dt.isoformat()})
                        
                        # پاکسازی ۲۴ ساعته (فقط پیام‌های قدیمی همین ربات)
                        day_ago = now_dt - timedelta(hours=24)
                        for old_msg in db["sent_msgs"][:]:
                            if datetime.fromisoformat(old_msg["time"]) < day_ago:
                                try:
                                    await client.delete_messages(MY_CHANNEL, [old_msg["id"]])
                                    db["sent_msgs"].remove(old_msg)
                                except: pass
                        
                        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                        await asyncio.sleep(15)

            await asyncio.sleep(30)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
