import asyncio
from telethon import events
from telethon import TelegramClient, sync

api_artem = "1203367"

hash_artem = "aef3f4bfbe501ee54a8b8ba68773e1b9"

client = TelegramClient('session_artem', api_artem, hash_artem)
client.start()

@client.on(events.NewMessage(outgoing=False, pattern=r'(?i).*(\bнайти|\bвзять|\bкупить|\bприобрести|\bдостать).*(\bреспиратор|\bмаск|\bперчатк|\bпатрон).*'))
async def handler(event):
    
    await event.reply('Тут! t.me/modern_selfcare_bot')



client.run_until_disconnected()

#+7 905 615 03 36