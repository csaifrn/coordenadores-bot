from discord.ext import commands
from decouple import config
import discord
import os


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def carregar_cogs():
    
    await bot.load_extension("manager")

    for file in os.listdir("Commands"):
        if file.endswith(".py"):
            cog = file[:-3]
            await  bot.load_extension(f'Commands.{cog}')

    for file in os.listdir("Tasks"):
        if file.endswith(".py"):
            cog = file[:-3]
            await  bot.load_extension(f'Tasks.{cog}')
      
      
@bot.event
async def on_ready():
    await carregar_cogs()
    await bot.tree.sync() 
    print(f'Bot está conectado.')
            
            

TOKEN = config("TOKEN")

bot.run(TOKEN)
