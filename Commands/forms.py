from discord.ext import commands
import discord
from discord import app_commands


class Registro_Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Registrar')

    nome = discord.ui.TextInput(label='Nome',placeholder='Digite seu nome')
    idade = discord.ui.TextInput(label='Idade',placeholder='Digite sua idade',style=discord.TextStyle.short)
    cor_favorito = discord.ui.TextInput(label='cor_favorita',placeholder='Digite sua cor favorita')

    
    async def on_submit(self, interaction:discord.Interaction):
        await interaction.response.send_message(f'Nome: {self.nome}\nIdade: {self.idade}\nSua cor favorita é : {self.cor_favorito}. ')    


class Form(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        super().__init__()

    @app_commands.command(description='Enviar forms')
    async def registrar(self,interaction:discord.Interaction):
        
        await interaction.response.send_modal(Registro_Modal())

async def setup(bot):
    await bot.add_cog(Form(bot)) 