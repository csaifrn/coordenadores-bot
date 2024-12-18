from discord.ext import commands
import requests
import discord
from discord import app_commands


class Crypto(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        super().__init__()

    
    @app_commands.command(description='Converter moeda!')
    async def send_coin(self,interaction:discord.Interaction,coin:str,base:str):
        try:
            response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}{base.upper()}')
            data = response.json()
            price= data.get("price")
            if price:
                await interaction.response.send_message(f'A moeda {coin} vale {price} em {base}')
            else:
                await interaction.response.send_message(f'O par {coin}/{base} é inválido')
        except Exception as error :
            await interaction.send(f'Está dando algum erro , espere até que seja normalizado!')
        

async def setup(bot):
    await bot.add_cog(Crypto(bot))  