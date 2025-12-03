from datetime import datetime, timedelta
import discord
from discord.ext import commands
import asyncio
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, button, Select, select

import asyncio
from bot_coordenador.coordenador_banco import (
    obter_duvidas, 
    registrar_resposta_no_banco,
    obter_duvidas_respondidas
)

class Coordenador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.usuario_atual = None
        self.atendimento_ativo = {}
        self.atendimento_pendente = {}

    @app_commands.command(description="Responder dúvidas!")
    async def proximo_atendimento(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if self.atendimento_ativo.get(user_id, False):
            await interaction.response.send_message(
                "Você já tem um atendimento em andamento. Por favor, continue o que você estava fazendo."
            )
            return
        self.atendimento_ativo[user_id] = True

    
        await interaction.response.send_message("Bem-vindo!")
        demanda_view = DemandaView(self.bot, self, user_id)
        message = await interaction.followup.send(view=demanda_view)
        demanda_view.message = message


class DemandaView(View):
    def __init__(self, bot, aluno_cog, user_id, timeout=600):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id = user_id
        self.show_interacao = ShowInteracao(self.bot, self.aluno_cog, self.user_id)

        if not self.aluno_cog.atendimento_pendente:
            self.remove_item(self.continuar_atendimento)
        else:
            self.remove_item(self.atender_proximo)

    async def disable_buttons_and_update(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.message = None

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True 
        if self.message:  
            await self.message.edit(
                content="Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/proximo_atendimento`.",
                view=self
            )
            self.aluno_cog.atendimento_ativo[self.user_id] = False
            del self.aluno_cog.atendimento_ativo[self.user_id]

    @button(label="Continuar Atendimento", style=discord.ButtonStyle.primary)
    async def continuar_atendimento(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        await self.show_interacao.atender_próximo(interaction)

    @button(label="Atender próximo", style=discord.ButtonStyle.primary)
    async def atender_proximo(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        await self.show_interacao.atender_próximo(interaction)

    @discord.ui.button(label="Atendimentos Aberto", style=discord.ButtonStyle.green)
    async def visualizar_abertos(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        duvida_pendente=self.aluno_cog.atendimento_pendente
        await self.show_interacao.show_visualizar_respostas_abertas(interaction, duvida_pendente)


    @discord.ui.button(label="Atendimentos Fechados", style=discord.ButtonStyle.red)
    async def visualizar_fechados(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        duvidas_com_respostas = obter_duvidas_respondidas()
        await self.show_interacao.show_visualizar_respostas_fechadas(interaction, duvidas_com_respostas)

    @button(label="Finalizar demanda", style=discord.ButtonStyle.danger)
    async def finalizar_demanda(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        self.aluno_cog.atendimento_ativo[self.user_id] = False 
        del self.aluno_cog.atendimento_ativo[self.user_id]
        await interaction.followup.send("Demanda finalizada com sucesso.")

class ShowInteracao():
    def __init__(self, bot, aluno_cog, user_id):
        super().__init__()
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id = user_id

    async def load_demanda_view(self, interaction):
        demanda_view = DemandaView(self.bot, self.aluno_cog, self.user_id)
        message = await interaction.followup.send(view=demanda_view)
        demanda_view.message = message

    
    async def gerenciar_timeout(self, interaction):
        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user, timeout=20)
            return msg
        except asyncio.TimeoutError:
            self.aluno_cog.atendimento_ativo[self.user_id] = False
            del self.aluno_cog.atendimento_ativo[self.user_id]

            await interaction.followup.send(
                "⏳ Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`."
            )
            return None
        
    async def atender_próximo(self, interaction: discord.Interaction):

        duvidas_status_local = {}

        if self.aluno_cog.atendimento_pendente:
            usuario_selecionado = next(iter(self.aluno_cog.atendimento_pendente))
            duvidas_status_local = self.aluno_cog.atendimento_pendente
        else:
            duvidas_agrupadas = obter_duvidas()

            if not duvidas_agrupadas:
                await interaction.user.send("✅ Não há dúvidas pendentes no momento.")
                await self.load_demanda_view(interaction)
                return

            usuario_selecionado = next(iter(duvidas_agrupadas))
            duvidas_usuario = list(duvidas_agrupadas[usuario_selecionado].keys())

            duvidas_status_local = {
                usuario_selecionado: {
                    titulo: {
                        "status": "Não Respondida",
                        "conteudo": duvidas_agrupadas[usuario_selecionado][titulo]
                    }
                    for titulo in duvidas_usuario
                }
            }
            self.aluno_cog.atendimento_pendente = duvidas_status_local

        while True:

            duvidas_usuario = list(duvidas_status_local[usuario_selecionado].keys())

            todas_respondidas = all(
                info["status"] == "Respondida" for info in duvidas_status_local[usuario_selecionado].values()
            )

            titulos_com_status = [
                f"{i + 1}. **{titulo}** {' - Respondida ✅' if duvidas_status_local[usuario_selecionado][titulo]['status'] == 'Respondida' else '- Não Respondida ❌'}"
                for i, titulo in enumerate(duvidas_usuario)
            ]

            lista_titulos = "\n".join([
                f"📝 **Dúvidas de {usuario_selecionado}:**\n",
                "\n".join(titulos_com_status) if titulos_com_status else "Nenhuma dúvida pendente.",
                "\n🔴 **Digite `0` para fechar o atendimento.**" if todas_respondidas else ""
            ])

            await interaction.user.send(
                f"{lista_titulos}\n\n"
                "🔎 **Escolha o número do título para responder a dúvida correspondente.**"
            )

            escolha_titulo = await self.gerenciar_timeout(interaction)
            if escolha_titulo is None:
                return
            escolha_titulo = escolha_titulo.content.strip()

            if escolha_titulo == "0":
                if todas_respondidas:
                    self.aluno_cog.atendimento_pendente = {}
                    await interaction.user.send("✅ Atendimento encerrado!")
                    await self.load_demanda_view(interaction)
                    break

            if not escolha_titulo.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue

            escolha_titulo_index = int(escolha_titulo) - 1

            if escolha_titulo_index < 0 or escolha_titulo_index >= len(duvidas_usuario):
                await interaction.user.send("Escolha inválida. Por favor, tente novamente.")
                continue

            titulo_selecionado = duvidas_usuario[escolha_titulo_index]
            duvida = duvidas_status_local[usuario_selecionado][titulo_selecionado]["conteudo"]

            mensagens = duvida['mensagem']
            resposta = duvida.get('resposta', '')
            data_duvida = duvida['timestamp_duvida']
            formatted_timestamp = data_duvida.split('.')[0]

            mensagem_resposta = (
                f"**📝 Dúvida Selecionada**\n"
                f"────────────────────────────────\n\n"
                f"**Título:** {titulo_selecionado}\n"
                f"**Data de Criação:** {formatted_timestamp}\n\n"
                f"**Mensagens:**\n"
                f"```{mensagens}```\n"
            )
            if resposta:
                mensagem_resposta += (
                    f"\n**Respostas Anteriores:**\n"
                    f"```{resposta}```\n"
                    "Deseja alterar a resposta? Digite **SIM** para alterar ou **NÃO** para manter:\n"
                )

            await interaction.user.send(mensagem_resposta)  # Envia apenas uma vez


            if resposta:
                

                while True:
                    escolha = await self.gerenciar_timeout(interaction)

                    if escolha is None:
                        return

                    escolha = escolha.content.strip().upper()

                    if escolha == "SIM":
                        break 
                    elif escolha == "NÃO":
                        await self.atender_próximo(interaction)  
                        return 
                    else:
                        await interaction.user.send("❌ Opção inválida! Digite **SIM** para alterar ou **NÃO** para manter.")


            await interaction.followup.send(f"\n✏️ Envie quantas mensagens forem necessárias para sua resposta.\n\n"
                                        "🔔 Quando terminar, digite uma única mensagem com `enviar` para encaminhar ao coordenador.\n")
        
            respostas = []
            while True:
                resposta = await self.gerenciar_timeout(interaction)

                if resposta is None:
                    return
                
                resposta = resposta.content.strip()

                if resposta.lower() == 'enviar':
                    if not respostas:
                        await interaction.user.send('⚠️ Você não adicionou nenhuma mensagem, sua resposta não foi salva!')
                        continue
                    break
                respostas.append(resposta)

            respostas_coordenador = "\n".join([f"{msg}" for msg in respostas])
            registrar_resposta_no_banco(usuario_selecionado, titulo_selecionado, respostas_coordenador)
            self.aluno_cog.atendimento_pendente[usuario_selecionado][titulo_selecionado]["status"] = "Respondida"
            self.aluno_cog.atendimento_pendente[usuario_selecionado][titulo_selecionado]['conteudo']["resposta"] = respostas_coordenador

            duvidas_status_local[usuario_selecionado] = self.aluno_cog.atendimento_pendente[usuario_selecionado]

            await interaction.followup.send(
                f"✅ **Respostas adicionadas com sucesso!**\n\n"
                f"📌 **Título:** {titulo_selecionado}\n\n"
                f"📝 **Respostas:**\n{respostas_coordenador}\n\n"
            )



    async def show_visualizar_respostas_abertas(self, interaction: discord.Interaction,duvidas):
        if not duvidas:
            await interaction.user.send("✅ Não há atendimento aberto.")
            await self.load_demanda_view(interaction)
            return


        usuario_selecionado = next(iter(duvidas))
        duvidas_status_local = duvidas

        while True:

            duvidas_usuario = list(duvidas_status_local[usuario_selecionado].keys())

            

            titulos_com_status = [
                f"{i + 1}. **{titulo}** {' - Respondida ✅' if duvidas_status_local[usuario_selecionado][titulo]['status'] == 'Respondida' else '- Não Respondida ❌'}"
                for i, titulo in enumerate(duvidas_usuario)
            ]

            lista_titulos = "\n".join([
                f"📝 **Dúvidas de {usuario_selecionado}:**\n",
                "\n".join(titulos_com_status) if titulos_com_status else "Nenhuma dúvida pendente.",
            ])

            await interaction.user.send(
                f"{lista_titulos}\n\n"
                "🔎 **Escolha o número do título para visualizar a dúvida correspondente.**"
            )

            escolha_titulo = await self.gerenciar_timeout(interaction)
            
            if escolha_titulo is None:
                return
            escolha_titulo = escolha_titulo.content.strip()

            

            if not escolha_titulo.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue

            escolha_titulo_index = int(escolha_titulo) - 1

            if escolha_titulo_index < 0 or escolha_titulo_index >= len(duvidas_usuario):
                await interaction.user.send("Escolha inválida. Por favor, tente novamente.")
                continue

            titulo_selecionado = duvidas_usuario[escolha_titulo_index]
            duvida = duvidas_status_local[usuario_selecionado][titulo_selecionado]["conteudo"] 

            mensagens = duvida['mensagem']
            resposta = duvida.get('resposta')  
            data_duvida = duvida['timestamp_duvida']
            formatted_timestamp = data_duvida.split('.')[0]


            mensagem_resposta = (
                f"**📝 Dúvida Selecionada**\n"
                f"────────────────────────────────\n\n"
                f"**Título:** {titulo_selecionado}\n"
                f"**Data de Criação:** {formatted_timestamp}\n\n"
                f"**Mensagens:**\n"
                f"```{mensagens}```\n"
            )

            if resposta:
                mensagem_resposta += (
                    f"\n**Respostas:**\n"
                    f"```{resposta}```\n"
                )

            await interaction.user.send(mensagem_resposta)

           
            await self.load_demanda_view(interaction)

            break

            
            
    

    async def show_visualizar_respostas_fechadas(self, interaction: discord.Interaction,duvidas):

        duvidas_com_respostas = duvidas

        if not duvidas_com_respostas:
            await interaction.user.send("Não há respostas registradas para exibir.")
            await self.load_demanda_view(interaction)
            return
        

        usuarios_com_respostas = list(duvidas_com_respostas.keys())
        lista_usuarios = "\n".join([f"{i + 1}. {user}" for i, user in enumerate(usuarios_com_respostas)])
        await interaction.user.send(
            f"Escolha um usuário para visualizar as respostas associadas às dúvidas:\n{lista_usuarios}"
        )

        while True:
            
            escolha_usuario  =await self.gerenciar_timeout(interaction)
        
            if escolha_usuario is None:
                return
            escolha_usuario = escolha_usuario.content.strip() 
            
            
            if not escolha_usuario.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue
            
        
            escolha_usuario_index = int(escolha_usuario) - 1

            if escolha_usuario_index < 0 or escolha_usuario_index >= len(usuarios_com_respostas):
                await interaction.user.send("Escolha inválida. Por favor, tente novamente.")
                continue

            usuario_selecionado = usuarios_com_respostas[escolha_usuario_index]
            duvidas_usuario = list(duvidas_com_respostas[usuario_selecionado].keys())
            lista_titulos = "\n".join([
                            f"{i + 1}. {titulo}"  
                            for i, titulo in enumerate(duvidas_usuario)  
                            ])

            
            await interaction.user.send(
                f"Escolha um título para visualizar as respostas:\n{lista_titulos}"
            )
            while True:
                

                escolha_titulo  = await self.gerenciar_timeout(interaction)
        
                if escolha_titulo is None:
                    return
                escolha_titulo = escolha_titulo.content.strip()
                
                
                if not escolha_titulo.isdigit():
                    await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                    continue
            

                escolha_titulo_index = int(escolha_titulo) - 1

                if escolha_titulo_index < 0 or escolha_titulo_index >= len(duvidas_usuario):
                    await interaction.user.send("Escolha inválida. Por favor, tente novamente.")
                    continue
                
                titulo_selecionado = duvidas_usuario[escolha_titulo_index]
                dados = duvidas_com_respostas[usuario_selecionado].get(titulo_selecionado)
                mensagens=dados.get("mensagem")
                respostas= dados.get("resposta")
                data_resposta=dados.get("timestamp_resposta")
                formatted_timestamp = data_resposta.split('.')[0]  

                await interaction.user.send(
                            f"**📝 Dúvida Selecionada**\n"
                            f"────────────────────────────────\n\n"
                            f"**Título:** {titulo_selecionado}\n"
                            f"**Data de Criação da resposta:** {formatted_timestamp}\n\n"
                            f"**Mensagens:**\n"
                            f"```{mensagens}```\n\n"
                            f"**Respostas:**\n"
                            f"```{respostas}```\n\n"
                            )
                
                await self.load_demanda_view(interaction)

                return


async def setup(bot):
    await bot.add_cog(Coordenador(bot))