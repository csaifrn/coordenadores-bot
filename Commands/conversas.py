from discord.ext import commands
import discord
from discord import app_commands

class Conversa(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        super().__init__()


    @app_commands.command(description='Diz olá!')
    async def send_hello(self,interaction: discord.Interaction):
        name = interaction.user.name
        response = f"Olá, {name}! 👋"
        await interaction.response.send_message(response,ephemeral=True)



async def setup(bot):
    await bot.add_cog(Conversa(bot))