from discord.ext import commands
import discord
from discord import app_commands

class Atendimento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.em_atendimento = None  
        self.fila = []  

    @app_commands.command(name="atendimento", description="Inicie um atendimento com o bot")
    async def atendimento(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                "Este comando só pode ser usado em mensagens diretas (DM). Envie uma mensagem para mim diretamente para iniciar o atendimento.",
                ephemeral=True
            )
            return

        if interaction.user in self.fila or interaction.user == self.em_atendimento:
            await interaction.user.send(
                "Você já está na fila de atendimento. Aguarde sua vez para ser atendido."
            )
            return

        if self.em_atendimento:
            self.fila.append(interaction.user)
            await interaction.user.send(
                f"Olá {interaction.user.name}, você foi adicionado à fila de atendimento. "
                f"Aguarde sua vez. Existem {len(self.fila)} pessoa(s) na sua frente."
            )
        else:
            await self.iniciar_atendimento(interaction.user)

    async def iniciar_atendimento(self, usuario: discord.User):
        self.em_atendimento = usuario
        await usuario.send(f"Olá {usuario.mention}, você agora está sendo atendido. Por favor, me diga sua dúvida.")
        await self.menu_interativo(usuario)

    async def iniciar_atendimento_proximo(self):
        if self.fila:
            proximo_usuario = self.fila.pop(0)
            await self.iniciar_atendimento(proximo_usuario)
        else:
            self.em_atendimento = None

    async def enviar_menu_inicial(self, usuario: discord.User):
        """Envia o menu inicial ao usuário por DM, apenas se for o usuário atualmente em atendimento."""
        if usuario != self.em_atendimento:
            await usuario.send("Aguarde sua vez para interagir com o menu.")
            return False

        meu_embed = discord.Embed(
            title='📋 Como posso te ajudar?',
            description='Escolha uma das opções abaixo digitando o número correspondente:',
            color=discord.Color.brand_green()
        )
        meu_embed.add_field(name='1️⃣ Como fazer chamado?', value='Guia para abrir chamados.', inline=False)
        meu_embed.add_field(name='2️⃣ Como colocar atestado?', value='Procedimento para adicionar atestados.', inline=False)
        meu_embed.add_field(name='3️⃣ Como se inscrever em auxílios?', value='Informações sobre inscrição em auxílios.', inline=False)

        try:
            await usuario.send(embed=meu_embed)
        except discord.Forbidden:
            print(f"Não foi possível enviar uma mensagem para {usuario.name}. O usuário pode ter desabilitado DMs.")
            return False
        except Exception as e:
            print(f"Erro ao enviar o menu inicial para {usuario.name}: {e}")
            return False

        return True

    async def obter_entrada_valida(self, usuario: discord.User, opcoes_validas: list) -> str:
        def check(m):
            return m.author == usuario and isinstance(m.channel, discord.DMChannel)

        while True:
            resposta = await self.bot.wait_for('message', check=check)
            if resposta.content in opcoes_validas:
                return resposta.content
            else:
                await usuario.send(f"Opção inválida. Por favor, escolha uma das opções válidas: {', '.join(opcoes_validas)}")

    async def menu_interativo(self, usuario: discord.User):
        enviado = await self.enviar_menu_inicial(usuario)
        if not enviado:
            return

        opcoes_iniciais = ['1', '2', '3']

        while True:
            escolha = await self.obter_entrada_valida(usuario, opcoes_iniciais)

            if escolha == '1':
                await usuario.send("Você escolheu 'Como fazer chamado?'. Aqui está o guia...")
            elif escolha == '2':
                await usuario.send("Você escolheu 'Como colocar atestado?'. Siga os passos...")
            elif escolha == '3':
                await usuario.send("Você escolheu 'Como se inscrever em auxílios?'. Veja os detalhes...")

            await self.enviar_menu_acao(usuario)
            opcoes_acao = ['1', '2']

            acao = await self.obter_entrada_valida(usuario, opcoes_acao)

            if acao == '1':
                await self.enviar_menu_inicial(usuario)  # Volta ao menu inicial
            elif acao == '2':
                await usuario.send("Espero ter ajudado! Até mais!")
                self.em_atendimento = None
                await self.iniciar_atendimento_proximo()
                break

async def setup(bot):
    await bot.add_cog(Atendimento(bot))
