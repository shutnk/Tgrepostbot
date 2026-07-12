from telethon import TelegramClient
from telethon.network import ConnectionTcpFull
import asyncio

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

MIRROR_HOST = '149.154.167.40'
MIRROR_PORT = 443

class MirrorConnection(ConnectionTcpFull):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ip = MIRROR_HOST
        self._port = MIRROR_PORT

async def main():
    client = TelegramClient(
        'session',
        API_ID,
        API_HASH,
        connection=MirrorConnection
    )
    await client.start()
    print("✅ Сессия сохранена через зеркальный сервер! Файл session.session готов.")
    await client.disconnect()

asyncio.run(main())
