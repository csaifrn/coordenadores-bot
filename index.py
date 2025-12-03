import discord
from discord.ext import commands
from decouple import config
import asyncio

# ============================
# CONFIGURAÇÃO DO BOT 1
# ============================

intents1 = discord.Intents.default()
intents1.message_content = True
intents1.members = True

bot1 = commands.Bot(command_prefix='!', intents=intents1)

async def setup_bot1():
    await bot1.load_extension("bot_coordenador.Commands.coordenador")
    print("[BOT 1] Extensões carregadas.")


@bot1.event
async def on_ready():
    print(f"[BOT 1] Logado como {bot1.user}")
    await bot1.tree.sync()
    print("[BOT 1] Slash commands sincronizados.")


# ============================
# CONFIGURAÇÃO DO BOT 2
# ============================

intents2 = discord.Intents.default()
intents2.message_content = True
intents2.members = True

bot2 = commands.Bot(command_prefix='?', intents=intents2)

async def setup_bot2():
    await bot2.load_extension("bot_aluno.Commands.aluno")
    print("[BOT 2] Extensões carregadas.")


@bot2.event
async def on_ready():
    print(f"[BOT 2] Logado como {bot2.user}")
    await bot2.tree.sync()
    print("[BOT 2] Slash commands sincronizados.")


# ============================
# INICIALIZAÇÃO DOS DOIS BOTS
# ============================

async def main():
    TOKEN1 = config("TOKEN1")
    TOKEN2 = config("TOKEN2")

    await setup_bot1()
    await setup_bot2()

    await asyncio.gather(
        bot1.start(TOKEN1),
        bot2.start(TOKEN2)
    )

if __name__ == "__main__":
    asyncio.run(main())
