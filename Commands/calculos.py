from discord.ext import commands
import discord
from discord import app_commands

class Calculo(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        super().__init__()

    @app_commands.command(description='Fazer cálculo')
    async def calculo(self,interaction:discord.Interaction,expression:str):
        valor = ''.join(expression)
        result = eval(valor)
        await interaction.response.send_message(f'A resposta é : ' + str(result))

    

async def setup(bot):
    await bot.add_cog(Calculo(bot)) 