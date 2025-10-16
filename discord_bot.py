import os
import sys
import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("SERVER_URL")
AUTHORIZED_IDS = os.getenv("AUTHORIZED_IDS", "")
AUTHORIZED_USERS = (
    set(int(id.strip()) for id in AUTHORIZED_IDS.split(",") if id.strip())
    if AUTHORIZED_IDS
    else set()
)

if DISCORD_BOT_TOKEN is None:
    print("ERRO: A variável de ambiente DISCORD_BOT_TOKEN não está definida.")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command(name="list_machines")
@commands.check(is_authorized)
async def list_machines(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/machines") as resp:
            if resp.status == 200:
                machines = await resp.json()
                if not machines:
                    await ctx.send("Nenhuma máquina ativa no momento.")
                    return
                msg = "**Máquinas ativas:**\n"
                for m in machines:
                    msg += f"- {m['id']} ({m['name']})\n"
                await ctx.send(msg)
            else:
                error_text = await resp.text()
                await ctx.send(
                    f"Erro ao consultar máquinas. Status: {resp.status}\nDetalhes: {error_text}"
                )


@list_machines.error
async def list_machines_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Você não tem permissão para usar este comando.")


@bot.command(name="register_script")
@commands.check(is_authorized)
async def register_script(ctx, name: str, *, content: str):
    payload = {"name": name, "content": content}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/scripts", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(data.get("message", "Script cadastrado com sucesso."))
            else:
                error = await resp.json()
                await ctx.send(f"Erro: {error.get('detail', 'Desconhecido')}")


@register_script.error
async def register_script_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Você não tem permissão para usar este comando.")
    else:
        await ctx.send("Uso correto: !register_script <nome> <conteúdo do script>")


@bot.command(name="execute_script")
@commands.check(is_authorized)
async def execute_script(ctx, machine_id: str, script_name: str):
    payload = {"machine_id": machine_id, "script_name": script_name}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/execute", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(data.get("message", "Comando agendado com sucesso."))
            else:
                error = await resp.json()
                await ctx.send(f"Erro: {error.get('detail', 'Desconhecido')}")


@execute_script.error
async def execute_script_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Você não tem permissão para usar este comando.")
    else:
        await ctx.send("Uso correto: !execute_script <nome_máquina> <nome_script>")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
