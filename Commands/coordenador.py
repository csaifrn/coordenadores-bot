from discord.ext import commands
import discord
from discord import app_commands
import asyncio
from datetime import datetime


from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, button


from Commands.aluno import duvidas_por_usuario  # Importa o dicionário compartilhado com as dúvidas

class Coordenador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.atendimento_ativo = {}  # Dicionário para controlar atendimentos ativos por usuário


    @app_commands.command(description="Visualizar títulos de dúvidas não respondidas e responder.")
    async def proximo_atendimento(self, interaction: discord.Interaction):

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
        
        await interaction.response.send_message("Bem-vindo!")




        class DemandaView(View):
            def __init__(self, bot,aluno_cog):
                super().__init__()
                self.bot = bot
                self.aluno_cog = aluno_cog

            @button(label="Atender próximo", style=discord.ButtonStyle.primary)
            async def atender_próximo(self, interaction: discord.Interaction, button):
                
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)


                # Filtra as dúvidas não respondidas
                duvidas_agrupadas = {}
                for usuario_name, duvidas in duvidas_por_usuario.items():
                    duvidas_sem_resposta = []
                    for titulo, dados in duvidas.items():
                        if not dados.get("respostas"):  # Verifica se não há respostas
                            duvidas_sem_resposta.append({"titulo": titulo, "dados": dados})
                    if duvidas_sem_resposta:
                        duvidas_agrupadas[usuario_name] = duvidas_sem_resposta

                # Agora, agrupando e ordenando as dúvidas de cada usuário com base no primeiro timestamp
                usuarios_com_duvidas = []

                for usuario_name, duvidas in duvidas_agrupadas.items():
                    # Obtém o menor timestamp entre as dúvidas do usuário
                    menor_timestamp = min(dados["dados"].get("timestamp", datetime.max) for dados in duvidas)
                    usuarios_com_duvidas.append((usuario_name, menor_timestamp, duvidas))  # Armazena o usuário, timestamp e as dúvidas

                # Ordena os usuários pelo timestamp mais antigo da primeira dúvida
                usuarios_com_duvidas.sort(key=lambda x: x[1])

                # Agora, extraímos os usuários ordenados com todas as dúvidas deles
                usuarios_com_duvidas_ordenadas = []

                for usuario_name, _, duvidas in usuarios_com_duvidas:
                    usuarios_com_duvidas_ordenadas.append((usuario_name, duvidas))



            
                if not usuarios_com_duvidas_ordenadas:
                    await interaction.followup.send("Não há dúvidas pendentes no momento.",view=DemandaView(self.bot, self.aluno_cog))
                    

                # Pegar o próximo usuário (primeiro da fila)
                usuario_selecionado = usuarios_com_duvidas_ordenadas[0][0]
                duvidas_usuario = duvidas_agrupadas[usuario_selecionado]

                
                lista_titulos = "\n".join([
                    f"{i + 1}. {item['titulo']}"
                    for i, item in enumerate(duvidas_usuario)
                ])
                while True:
                    await interaction.followup.send(
                        f"Dúvidas de {usuario_selecionado}:\n{lista_titulos}\n"
                        "Escolha um título pela posição na lista para visualizar as mensagens."
                    )

                    escolha_titulo = await self.bot.wait_for('message')
                    
                
                    if not escolha_titulo.content.isdigit():  # Verifica se não é um número
                        await interaction.followup.send("Escolha inválida. Por favor, envie um número.")
                    
                    else:
                        escolha_titulo_index = int(escolha_titulo.content) - 1

                        if escolha_titulo_index < 0 or escolha_titulo_index >= len(duvidas_usuario):
                            await interaction.followup.send("Escolha inválida. Por favor, tente novamente.")
                        else:

                            titulo_selecionado = duvidas_usuario[escolha_titulo_index]
                            titulo = titulo_selecionado["titulo"]
                            dados = titulo_selecionado["dados"]
                            
                            mensagens = dados.get("mensagens", [])
                            nome = dados.get("nome")
                            matricula = dados.get("matricula")

                            mensagens_formatadas = "\n".join([f"- {msg}" for msg in mensagens]) if mensagens else "Nenhuma mensagem registrada."

                            await interaction.followup.send(
                                f"**Nome:** {nome}\n**Matrícula:** {matricula}\n"
                                 f"**Título : {titulo}**\n"
                                f"**Mensagens:**\n{mensagens_formatadas}\n\n"
                                "Agora você pode responder a essa dúvida. Envie suas respostas.\n"
                                "Digite 'enviar' para encerrar."
                            )

                            respostas = []
                            while True:
                                resposta_msg = await self.bot.wait_for('message')
                                resposta = resposta_msg.content

                                if resposta.lower() == 'enviar':
                                    break
                                
                                respostas.append(resposta)

                            # Adicionar respostas ao título
                            dados["respostas"].extend(respostas)
                            await interaction.followup.send(
                                f"Respostas adicionadas ao título **{titulo}**:\n"
                                f"{chr(10).join([f'- {r}' for r in respostas])}\n"
                                f"O título foi atualizado com as novas respostas.\n\n", view=DemandaView(self.bot, self.aluno_cog)
                            )
                            break
                


            @button(label="Visualizar respostas", style=discord.ButtonStyle.secondary)
            async def visualizar_respostas(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)

                # Filtra as dúvidas que possuem respostas
                duvidas_com_respostas = {}

                for usuario_name, duvidas in duvidas_por_usuario.items():
                    duvidas_com_resposta = []
                    for titulo, dados in duvidas.items():
                        if dados.get("respostas"):  # Verifica se há respostas
                            duvidas_com_resposta.append({"titulo": titulo, "dados": dados})
                    if duvidas_com_resposta:
                        duvidas_com_respostas[usuario_name] = duvidas_com_resposta

                if not duvidas_com_respostas:
                    await interaction.followup.send("Não há respostas registradas para exibir.")
                    return

                # Lista usuários com dúvidas respondidas
                usuarios_com_respostas = list(duvidas_com_respostas.keys())
                lista_usuarios = "\n".join([f"{i + 1}. {user}" for i, user in enumerate(usuarios_com_respostas)])

                cancelado=False

                while not cancelado:
                    await interaction.followup.send(
                        f"Escolha um usuário para visualizar as respostas associadas às dúvidas:\n{lista_usuarios}"
                    )

                    escolha_usuario = await self.bot.wait_for('message')

                    if not escolha_usuario.content.isdigit():
                        await interaction.followup.send("Escolha inválida. Por favor, envie um número.")
                    
                    else:

                        escolha_usuario_index = int(escolha_usuario.content) - 1

                        if escolha_usuario_index < 0 or escolha_usuario_index >= len(usuarios_com_respostas):
                            await interaction.followup.send("Escolha inválida. Por favor, tente novamente.")
                        else:


                            usuario_selecionado = usuarios_com_respostas[escolha_usuario_index]
                            duvidas_usuario = duvidas_com_respostas[usuario_selecionado]

                            # Lista títulos de dúvidas respondidas
                            
                            lista_titulos = "\n".join([f"{i + 1}. {item['titulo']}" for i, item in enumerate(duvidas_usuario)])

                            while True:
                            
                                await interaction.followup.send(
                                    f"Escolha um título para visualizar as respostas:\n{lista_titulos}"
                                )

                                escolha_titulo = await self.bot.wait_for('message')

                                if not escolha_titulo.content.isdigit():
                                    await interaction.followup.send("Escolha inválida. Por favor, envie um número.")
                                else:

                                    escolha_titulo_index = int(escolha_titulo.content) - 1

                                    if escolha_titulo_index < 0 or escolha_titulo_index >= len(duvidas_usuario):
                                        await interaction.followup.send("Escolha inválida. Por favor, tente novamente.")
                                    else:

                                        titulo_selecionado = duvidas_usuario[escolha_titulo_index]
                                        titulo = titulo_selecionado["titulo"]
                                        dados = titulo_selecionado["dados"]
                                        mensagens= dados.get("mensagens", [])
                                        respostas = dados.get("respostas", [])
                                        nome = dados.get("nome")
                                        matricula = dados.get("matricula")

                                        mensagens_formatadas = "\n".join(
                                        [f"- {msg}" for msg in mensagens]) if mensagens else "Nenhuma mensagem registrada."
                                        respostas_formatadas = "\n".join(
                                        [f"- {resp}" for resp in respostas]) if respostas else "Nenhuma resposta registrada."

                                                    
                                        await interaction.followup.send(
                                            f"**Nome:** {nome}\n**Matrícula:** {matricula}\n"
                                            f"**Título:** {titulo}\n"
                                            f"**Mensagens:**\n{mensagens_formatadas}\n\n"
                                            f"**Respostas:**\n{respostas_formatadas}\n\n",view=DemandaView(self.bot, self.aluno_cog))

                                       
                                        cancelado=True
                                        break
                                                
            @button(label="Finalizar demanda", style=discord.ButtonStyle.danger)
            async def finalizar_demanda(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)


                self.aluno_cog.atendimento_ativo.pop(interaction.user.id, None)

                await interaction.followup.send(
                    "Demanda finalizada com sucesso."
                )
                
                 
        await interaction.followup.send(view=DemandaView(self.bot, self))

async def setup(bot):
    await bot.add_cog(Coordenador(bot))
