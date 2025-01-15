import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, button
from datetime import datetime

duvidas_por_usuario = {}

class Aluno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.atendimento_ativo = {}  # Dicionário para controlar atendimentos ativos por usuário

    @app_commands.command(description='Inicia o atendimento e captura as mensagens com um título definido pelo usuário.')
    async def iniciar_atendimento(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Verifica se o usuário já tem um atendimento ativo
        if self.atendimento_ativo.get(user_id):
            await interaction.response.send_message(
                "Você já tem um atendimento em andamento. Por favor, finalize o atendimento atual antes de iniciar outro.",
                ephemeral=True
            )
            return

        # Marca o atendimento como ativo
        self.atendimento_ativo[user_id] = True
        await interaction.response.send_message("Bem-vindo! Vamos iniciar o atendimento. Por favor, digite seu nome completo.")

        nome_msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
        nome = nome_msg.content.strip()

        await interaction.followup.send("Agora, por favor, digite sua matrícula.")
        matricula_msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
        matricula = matricula_msg.content.strip()

        class MenuView(View):
            def __init__(self, bot, aluno_cog):
                super().__init__()
                self.bot = bot
                self.aluno_cog = aluno_cog  # Referência ao cog Aluno para acessar o atendimento_ativo

            @button(label="Adicionar nova dúvida", style=discord.ButtonStyle.primary)
            async def adicionar_duvida(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)

                await interaction.followup.send("Por favor, digite o título da sua dúvida.")
                titulo_msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
                titulo = titulo_msg.content.strip()

                if interaction.user.name not in duvidas_por_usuario:
                    duvidas_por_usuario[interaction.user.name] = {}
                duvidas_por_usuario[interaction.user.name][titulo] = {
                    "nome": nome,
                    "matricula": matricula,
                    "mensagens": [],
                    "respostas": [],
                    "timestamp": datetime.now()  # Adiciona timestamp
                }

                await interaction.followup.send(
                    f"Título registrado: **{titulo}**. Agora você pode digitar as mensagens da sua dúvida. "
                    "Envie quantas mensagens quiser. Para enviar ao coordenador, envie uma mensagem com 'enviar'."
                )

                while True:
                    mensagem = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)

                    if mensagem.content.lower() == "enviar":
                        break

                    duvidas_por_usuario[interaction.user.name][titulo]["mensagens"].append(mensagem.content)

                await interaction.followup.send(view=MenuView(self.bot, self.aluno_cog))

            @button(label="Visualizar dúvidas", style=discord.ButtonStyle.secondary)
            async def visualizar_duvidas(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)

                user_name = interaction.user.name
                user_duvidas = duvidas_por_usuario.get(user_name)

                if not user_duvidas:
                    await interaction.followup.send('Não há nenhuma dúvida.')
                    await interaction.followup.send(view=MenuView(self.bot, self.aluno_cog))
                    return

                titulos = list(user_duvidas.keys())
                enumeracao = "\n".join([f"{i + 1}. {titulo}" for i, titulo in enumerate(titulos)])

                while True:
                    await interaction.followup.send(
                        f"Escolha o número de um título para visualizar as mensagens e respostas associadas:\n{enumeracao}"
                    )

                    escolha = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user)

                    if not escolha.content.isdigit():
                        await interaction.followup.send("Escolha inválida. Por favor, envie um número.")
                    else:
                        escolha_index = int(escolha.content) - 1

                        if escolha_index < 0 or escolha_index >= len(titulos):
                            await interaction.followup.send("Escolha inválida. Por favor, escolha um número válido.")
                        else:
                            titulo_escolhido = titulos[escolha_index]
                            dados = user_duvidas.get(titulo_escolhido, {})
                            mensagens = dados.get("mensagens", [])
                            respostas = dados.get("respostas", [])
                            nome = dados.get("nome")
                            matricula = dados.get("matricula")

                            mensagens_formatadas = "\n".join(
                                [f"- {msg}" for msg in mensagens]) if mensagens else "Nenhuma mensagem registrada."
                            respostas_formatadas = "\n".join(
                                [f"- {resp}" for resp in respostas]) if respostas else "Nenhuma resposta registrada."

                            await interaction.followup.send(
                                f"**Nome:** {nome}\n**Matrícula:** {matricula}\n"
                                f"**Título:** {titulo_escolhido}\n"
                                f"**Mensagens:**\n{mensagens_formatadas}\n\n"
                                f"**Respostas:**\n{respostas_formatadas}\n\n",
                                view=MenuView(self.bot, self.aluno_cog)
                            )
                            break

            @button(label="Finalizar atendimento", style=discord.ButtonStyle.danger)
            async def finalizar_atendimento(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)

                self.aluno_cog.atendimento_ativo.pop(interaction.user.id, None)

                await interaction.followup.send("Atendimento finalizado com sucesso! Você pode iniciar um novo atendimento com o comando `/iniciar_atendimento`.")

        await interaction.followup.send(view=MenuView(self.bot,  self))
        

async def setup(bot):
    await bot.add_cog(Aluno(bot))
