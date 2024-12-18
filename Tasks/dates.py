from discord.ext import commands,tasks
import discord
from datetime import datetime


class Date(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        super().__init__()
        self.current_time.start()

    @tasks.loop(minutes=10)
    async def current_time(self):
        now = datetime.now()
        now = now.strftime("%d/%m/%Y às %H:%M:%S")
        for guild in self.bot.guilds:
            for channel in guild.text_channels:  
                try:
                    await channel.send(f'Data e hora: {now}')
                except discord.Forbidden:
                    pass

    

async def setup(bot):
    await bot.add_cog(Date(bot)) 