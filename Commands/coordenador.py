from discord.ext import commands
import discord
from discord import app_commands
import asyncio

from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, button


from Commands.aluno import duvidas_por_usuario  # Importa o dicionário compartilhado com as dúvidas

class Coordenador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Visualizar títulos de dúvidas não respondidas e responder.")
    async def proximo_atendimento(self, interaction: discord.Interaction):
        
        await interaction.response.send_message("Bem-vindo!")




        class DemandaView(View):
            def __init__(self, bot):
                super().__init__()
                self.bot = bot

            @button(label="Atender próximo", style=discord.ButtonStyle.primary)
            async def atender_próximo(self, interaction: discord.Interaction, button):
                
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)


                duvidas_agrupadas = {
                    usuario_id: [
                        {"titulo": titulo, "dados": dados}
                        for titulo, dados in duvidas.items()
                        if not dados.get("respostas")  # Apenas dúvidas sem respostas
                    ]
                    for usuario_id, duvidas in duvidas_por_usuario.items()
                }

                usuarios_com_duvidas = sorted(
                (uid for uid, duvidas in duvidas_agrupadas.items() if duvidas),
                key=lambda uid: min(
                    duvida["dados"].get("timestamp", float("inf"))
                    for duvida in duvidas_agrupadas[uid]
                )

                )
                
                print(duvidas_agrupadas)
                print(usuarios_com_duvidas)

            
                if not usuarios_com_duvidas:
                    await interaction.followup.send("Não há dúvidas pendentes no momento.")
                    return

                # Pegar o próximo usuário (primeiro da fila)
                usuario_selecionado = usuarios_com_duvidas[0]
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
                                "O título foi atualizado com as novas respostas.", view=DemandaView(self.bot)
                            )
                            break
                


            
            @button(label="Finalizar demanda", style=discord.ButtonStyle.danger)
            async def finalizar_demanda(self, interaction: discord.Interaction, button):
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(view=self)
                del self.atendimento_ativo[interaction.user.name]  # Remove o usuário do atendimento ativo
                await interaction.followup.send(
                    "Demanda finalizada com sucesso."
                )
                
                 
        await interaction.followup.send(view=DemandaView(self.bot))

async def setup(bot):
    await bot.add_cog(Coordenador(bot))
