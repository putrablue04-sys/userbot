import asyncio, json, os
from telethon import TelegramClient
from telethon.events import NewMessage

api_id = 33949314
api_hash = '87b0593e2015718c550f04e0e49c2733'

DELAY = 10
MESSAGE_TEXT = "🚀 Promo jalan terus!"
GROUP_FILE = 'groups.json'

send_task = None

# =====================
# UTIL JSON (AMAN)
# =====================
def load_groups():
    if not os.path.exists(GROUP_FILE):
        return set()
    try:
        with open(GROUP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('groups', []))
    except json.JSONDecodeError:
        return set()

def save_groups(groups):
    with open(GROUP_FILE, 'w', encoding='utf-8') as f:
        json.dump({"groups": list(groups)}, f, indent=2)

TARGET_GROUPS = load_groups()

# =====================
# AUTO SEND
# =====================
async def auto_send(client):
    while True:
        for gid in list(TARGET_GROUPS):
            try:
                await client.send_message(gid, MESSAGE_TEXT)
                await asyncio.sleep(1)
            except Exception as e:
                print(f'Gagal kirim ke {gid}:', e)
        await asyncio.sleep(DELAY)

# =====================
# MAIN
# =====================
async def main():
    global send_task, DELAY

    client = TelegramClient('session', api_id, api_hash)
    await client.start()
    print('🔥 Userbot promosi aktif')

    @client.on(NewMessage(pattern='/ping'))
    async def ping(event):
        await event.reply('✅ USERBOT AKTIF')

    @client.on(NewMessage(pattern='/addgroup'))
    async def add_group(event):
        TARGET_GROUPS.add(event.chat_id)
        save_groups(TARGET_GROUPS)
        await event.delete()

    @client.on(NewMessage(pattern='/removegroup'))
    async def remove_group(event):
        TARGET_GROUPS.discard(event.chat_id)
        save_groups(TARGET_GROUPS)
        await event.delete()

    @client.on(NewMessage(pattern='/listgroup'))
    async def list_group(event):
        if not TARGET_GROUPS:
            await event.reply('📭 Belum ada grup target')
            return

        text = "📋 DAFTAR GRUP TARGET:\n\n"
        for i, gid in enumerate(TARGET_GROUPS, 1):
            text += f"{i}. {gid}\n"

        await event.reply(text)

    @client.on(NewMessage(pattern='/startsend'))
    async def start_send(event):
        global send_task
        if send_task:
            await event.reply('⚠️ Auto send sudah jalan')
            return
        send_task = asyncio.create_task(auto_send(client))
        await event.reply(f'▶️ Auto send dimulai\nDelay: {DELAY} detik')

    @client.on(NewMessage(pattern='/stopsend'))
    async def stop_send(event):
        global send_task
        if send_task:
            send_task.cancel()
            send_task = None
            await event.reply(' Auto send dihentikan')
        else:
            await event.reply('Auto send belum aktif')

    @client.on(NewMessage(pattern=r'/setdelay (\d+)'))
    async def set_delay(event):
        global DELAY
        DELAY = int(event.pattern_match.group(1))
        await event.reply(f'⏱ Delay diubah ke {DELAY} detik')

    try:
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        print('Userbot dihentikan')

    

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Userbot dimatikan')


