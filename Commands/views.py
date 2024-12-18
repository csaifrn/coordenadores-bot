from discord.ext import commands
import discord
from discord import app_commands


class ViewCumprimento(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)



    @discord.ui.select(custom_id='comida_favorita', placeholder='Selecione sua comida favorita!', options=[
        discord.SelectOption(label='Pizza', value='1'),
        discord.SelectOption(label='Brigadeiro', value='2'),
        discord.SelectOption(label='Bolo', value='3'),
        discord.SelectOption(label='Sorvete', value='4'),
        discord.SelectOption(label='Biscoito', value='5')
    ])

    async def comida_favorita(self, interaction: discord.Interaction, select: discord.ui.Select):
        comida_selecionada = select.values[0]
        
        comidas = {
            '1': 'Pizza',
            '2': 'Brigadeiro',
            '3': 'Bolo',
            '4': 'Sorvete',
            '5': 'Biscoito'
        }

        nome_comida = comidas.get(comida_selecionada, 'Desconhecida')
        
        await interaction.response.send_message(f"Sua comida favorita é {nome_comida}")

    
    

class View(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        super().__init__()
        self.menu=ViewCumprimento()



    @app_commands.command(description='Menu para escolher comida favorita!')
    async def menu_comida(self,interaction : discord.Interaction):

        await interaction.response.send_message(view=self.menu)



    @app_commands.command(description='Mostrar botões!')
    async def enviar_botao(self, interaction:discord.Interaction):
        async def resposta_botao(interaction:discord.Interaction):
            await interaction.response.send_message('Botão pressionado',ephemeral=True)

        view= discord.ui.View()
        botao=discord.ui.Button(label='Botão',style=discord.ButtonStyle.green)
        botao_url=discord.ui.Button(label='Botão.',style=discord.ButtonStyle.primary, url='https://suap.ifrn.edu.br/accounts/login/?next=/')

        botao.callback=resposta_botao

        view.add_item(botao)
        view.add_item(botao_url)

        await interaction.response.send_message(view=view)


    @app_commands.command(description='Menu para escolher cor favorita!')
    @app_commands.choices(cor=[
        app_commands.Choice(name='AZUL',value='BA2D0B'),
        app_commands.Choice(name='VERMELHO',value='22577A')
    ])
    async def escolha_cor(self,interaction: discord.Interaction,cor:app_commands.Choice[str]):
        await interaction.response.send_message(f'A cor escolhida foi {cor.name} : {cor.value}')
    


async def setup(bot):
    bot.add_view(ViewCumprimento())
    await bot.add_cog(View(bot))

