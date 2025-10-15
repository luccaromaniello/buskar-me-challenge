import discord
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "").split(",")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if str(message.author.id) not in AUTHORIZED_USERS or message.author == client.user:
        await message.channel.send("❌ Você não tem permissão.")
        return

    if message.content.startswith("!list_machines"):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/machines") as resp:
                data = await resp.json()
                msg = "\n".join([f"{m['name']} (ID: {m['id']})" for m in data])
                await message.channel.send(msg or "Nenhuma máquina ativa.")

# Implemente os outros comandos depois
client.run(TOKEN)
