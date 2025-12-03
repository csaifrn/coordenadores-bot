
from datetime import datetime,timedelta
import time
import discord
from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, button,Select, select

import asyncio
from bot_aluno.aluno_banco import (
registrar_duvida_no_banco,
registrar_aluno_no_banco,
atualizar_mensagens,
atualizar_visualizada,
deletar_duvida,
obter_duvidas,verificar_duplicidade)


class Aluno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.atendimento_ativo = {}
  
    
    @app_commands.command(description='Inicia o atendimento e captura as mensagens com um título definido pelo usuário.')
    async def iniciar_atendimento(self, interaction: discord.Interaction):

        user_id=interaction.user.id

        if self.atendimento_ativo.get(user_id,False):
            await interaction.response.send_message(
                "Você já tem um atendimento em andamento. Por favor, continue o que você estava fazendo."
            )
            return
        
        self.atendimento_ativo[user_id]=True

        user_name = interaction.user.name
       
        registrar_aluno_no_banco(user_name)
            
        duvidas_nao_visualizadas = obter_duvidas(user_name,None,"duvidas_nao_visualizadas")

        await interaction.response.send_message('Bem-vindo!')

        def numero_para_emoji(numero):
            emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            return ''.join(emojis[int(digito)] for digito in str(numero))

        if duvidas_nao_visualizadas:
                lista_duvidas = "\n".join(
                    [f"{numero_para_emoji(index + 1)} **{titulo}**" for index, titulo in enumerate(duvidas_nao_visualizadas.keys())]
                )            
                await interaction.followup.send(
                        "🔔 ATENÇÃO VOCÊ TEM DÚVIDAS QUE JÁ FORAM RESPONDIDAS E NÃO VISUALIZADAS\n\n"
                        f"Lista de dúvidas\n"
                        f"{lista_duvidas}\n\n"
                        f"Acesse o menu de visualizar dúvidas!"
                    )

        menu_view = Menu(self.bot, self,user_id)
        message = await interaction.followup.send(view=menu_view)
        menu_view.message = message 
        
class Menu(View):
    def __init__(self, bot, aluno_cog,user_id, timeout=600):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id=user_id
        self.show_interacao = ShowInteracao(self.bot, self.aluno_cog,self.user_id)


    async def on_timeout(self):
        for item in self.children:
            item.disabled = True 
        if self.message:
            await self.message.edit(content="Tempo esgotado ! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`.",view=None)
            del self.aluno_cog.atendimento_ativo[self.user_id]
            return
        
    async def load_filtro_duvidas(self,interaction,tipo,resposta):
        menu_view = FiltroDuvidas(self.bot, self.aluno_cog,tipo,resposta,self.user_id)
        message = await interaction.followup.send(view=menu_view)
        menu_view.message = message
        
    async def load_duvidas(self,interaction):
        menu_view =  Duvidas(self.bot, self.aluno_cog,self.user_id)
        message = await interaction.followup.send(view=menu_view)
        menu_view.message = message
        
    async def disable_buttons_and_update(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.message=None
        
    @button(label="Adicionar dúvida", style=discord.ButtonStyle.primary)
    async def adicionar_duvida(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        await self.show_interacao.adicionar_duvida(interaction)


    @button(label="Visualizar dúvidas", style=discord.ButtonStyle.secondary)
    async def visualizar_duvidas(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        await self.load_duvidas(interaction)


    @button(label="Editar Dúvida", style=discord.ButtonStyle.success)
    async def editar_dúvida(self, interaction: discord.Interaction,button):
        await self.disable_buttons_and_update(interaction)
        await self.load_filtro_duvidas(interaction,"editar","duvidas_sem_resposta")
 

    @button(label="Deletar Dúvida", style=discord.ButtonStyle.danger)
    async def deletar_duvida(self, interaction: discord.Interaction, button):
        await self.disable_buttons_and_update(interaction)
        await self.load_filtro_duvidas(interaction,"deletar","duvidas_sem_resposta")
     
        
class Submenu(View):
    def __init__(self, bot, aluno_cog,user_id,timeout=600):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id=user_id

    async def disable_buttons_and_update(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.message=None


    async def on_timeout(self):
        for item in self.children:
            item.disabled = True  
        if self.message:    
            await self.message.edit(content="Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`.",view=self)
            del self.aluno_cog.atendimento_ativo[self.user_id]
            return
        
    @button(label="Finalizar atendimento", style=discord.ButtonStyle.danger)
    async def finalizar_atendimento(self, interaction: discord.Interaction, button):
        
        await self.disable_buttons_and_update(interaction)
        del self.aluno_cog.atendimento_ativo[self.user_id]
        await interaction.followup.send("Atendimento finalizado com sucesso! Você pode iniciar um novo atendimento com o comando `/iniciar_atendimento`.")

        
    @button(label="Voltar ao menu principal", style=discord.ButtonStyle.primary)
    async def voltar_menu(self, interaction: discord.Interaction, button):
        
        await self.disable_buttons_and_update(interaction)
        menu_view = Menu(self.bot, self.aluno_cog,self.user_id)
        message = await interaction.followup.send(view=menu_view)
        menu_view.message = message


    
class Duvidas(View):
    def __init__(self, bot, aluno_cog,user_id,timeout=10):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id=user_id

    async def disable_and_update(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.message=None

    async def load_filtro_duvidas(self,interaction,resposta):
        menu_view = FiltroDuvidas(self.bot, self.aluno_cog,"visualizar",resposta,self.user_id)
        message = await interaction.user.send(view=menu_view)
        menu_view.message = message


    async def on_timeout(self):
        for item in self.children:
            item.disabled = True  
        if self.message:    
            await self.message.edit(content="Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`.",view=self)
            del self.aluno_cog.atendimento_ativo[self.user_id]
            return
            
    
    @select(
        placeholder="Selecione o tipo de resposta para filtrar",
        options=[
            discord.SelectOption(label="Não Respondidas", value="nao_respondidas", description="Dúvidas que não foram respondidas."),
            discord.SelectOption(label="Respondidas", value="respondidas", description="Dúvidas que já foram respondidas."),
        ],
        custom_id="filtro_duvidas"
    )
    async def filtro_duvidas(self, interaction: discord.Interaction, select: Select):
        await self.disable_and_update(interaction)

        if select.values[0] == "nao_respondidas":
            await self.load_filtro_duvidas(interaction,"duvidas_sem_resposta")
        elif select.values[0] == "respondidas":
            await self.load_filtro_duvidas(interaction,"duvidas_com_resposta")
    

class FiltroDuvidas(View):
    def __init__(self, bot, aluno_cog, tipo,resposta,user_id,timeout=10):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.tipo=tipo
        self.resposta=resposta
        self.user_id=user_id
        self.show_interacao = ShowInteracao(self.bot, self.aluno_cog,self.user_id)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True  
        if self.message:    
            await self.message.edit(content="Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`.",view=self)
             
            del self.aluno_cog.atendimento_ativo[self.user_id]
            return

    async def disable_and_update(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.message = None
    
    @select(
        placeholder="Selecione o período para filtrar as dúvidas...",
        options=[
            discord.SelectOption(label="Hoje", value="hoje", description="Dúvidas de hoje", emoji="📅"),
            discord.SelectOption(label="Últimos 7 dias", value="7_dias", description="Dúvidas dos últimos 7 dias", emoji="📆"),
            discord.SelectOption(label="Últimos 30 dias", value="30_dias", description="Dúvidas dos últimos 30 dias", emoji="🗓️"),
            discord.SelectOption(label="Todas", value="todas", description="Todas as dúvidas", emoji="🔍")
        ],
        custom_id="menu_filtro"
    )
    async def menu_filtro(self, interaction: discord.Interaction, select: Select):
        await self.disable_and_update(interaction)

        if select.values[0] == "hoje":
            inicio_periodo = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif select.values[0] == "7_dias":
            inicio_periodo = datetime.now() - timedelta(days=7)
        elif select.values[0] == "30_dias":
            inicio_periodo = datetime.now() - timedelta(days=30)
        else:
            inicio_periodo = None  


        duvidas = obter_duvidas(interaction.user.name, inicio_periodo,self.resposta)


        if self.tipo=='editar':
           await self.show_interacao.show_editar_duvidas(interaction,duvidas)
        elif self.tipo=='visualizar':
            await self.show_interacao.show_duvidas(interaction,duvidas)
        elif self.tipo=='deletar':
            await self.show_interacao.show_deletar_duvidas(interaction,duvidas)



class ShowInteracao():
    def __init__(self, bot, aluno_cog,user_id):
        super().__init__()
        self.bot = bot
        self.aluno_cog = aluno_cog
        self.user_id=user_id


    async def load_submenu(self,interaction):
        menu_view =  Submenu(self.bot, self.aluno_cog,self.user_id)
        message = await interaction.followup.send(view=menu_view)
        menu_view.message = message
        menu_view.user_id=self.user_id

    async def gerenciar_timeout(self, interaction):
        try:
            while True:

                titulo = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user, timeout=600)
                
                if titulo.attachments:
                    await interaction.user.send(
                        "❌ **Erro:** Apenas **mensagens de texto** são permitidas. 🚫 Arquivos ou imagens não são aceitos. 📎"
                    )
                    continue  

                return titulo
                
        except asyncio.TimeoutError:

            
            del self.aluno_cog.atendimento_ativo[self.user_id]
            await interaction.user.send(
                "Tempo esgotado! O atendimento foi encerrado. Você pode iniciar novamente usando `/iniciar_atendimento`."
            )
            return None

    
    

    async def adicionar_duvida(self, interaction: discord.Interaction):

        await interaction.followup.send("Por favor, digite o título da sua dúvida.")
        while True:

            titulo = await self.gerenciar_timeout(interaction)
            
            if titulo is None:
                await interaction.followup.send('⚠️ Como você não adicionou nenhum tútulo , sua dúvida não foi aceita!')

                return
            
            titulo = titulo.content.strip()    
            duplicidade_titulo=verificar_duplicidade(interaction.user.name,titulo)
            if duplicidade_titulo:
                await interaction.user.send(
                "⚠️ **Aviso:** Você já possui uma dúvida registrada com este título.\n"
                "Por favor, escolha um título diferente para a sua nova dúvida."
            )
            else:
                break


        await interaction.user.send(
            f"✅ **Título registrado com sucesso:** **{titulo}**\n\n"
            "📨 Agora você pode digitar as mensagens da sua dúvida.\n"
            "✏️ Envie quantas mensagens forem necessárias para explicar sua dúvida.\n\n"
            "🔔 **Quando terminar, digite uma única mensagem com** `enviar` **para encaminhar ao coordenador.**\n\n"
        )


        mensagens=[]
        while True:    

            mensagem= await self.gerenciar_timeout(interaction)
            
            if mensagem is None:
                deletar_duvida(interaction.user.name,titulo)
                await interaction.user.send('⚠️ Como você não adicionou nenhuma mensagem , sua dúvida não foi aceita!')
                return
            mensagem =mensagem.content.strip()

            if mensagem.lower() == "enviar":
                if len(mensagens)==0:
                    deletar_duvida(interaction.user.name,titulo)

                    await interaction.user.send('⚠️ Como você não adicionou nenhuma mensagem , sua dúvida não foi aceita!')
                    await  self.load_submenu(interaction) 

                    return 

                break
            mensagens.append(mensagem)

        mensagem_unica="\n".join([f"{msg}" for msg in mensagens])

        registrar_duvida_no_banco(interaction.user.name, titulo, mensagem_unica)
        await  self.load_submenu(interaction)

        return 

    async def show_duvidas(self, interaction, duvidas):
        if not duvidas:
            await interaction.followup.send("Não há nenhuma dúvida.")
            await self.load_submenu(interaction)
            return
        

        titulos = list(duvidas.keys())
        enumeracao_titulos = "\n".join([f"{i + 1}. {titulo}" for i, titulo in enumerate(titulos)])  
        await interaction.followup.send(
                f"Escolha o número de um título para visualizar as mensagens e respostas associadas:\n{enumeracao_titulos}\n99.Mostrar todas"
            )
        while True:
            escolha = await self.gerenciar_timeout(interaction)

            if escolha is None:
                return
            escolha = escolha.content.strip()

            if not escolha.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue

            escolha_index = int(escolha) - 1
            if escolha_index == 98:  
                for titulo, dados in duvidas.items():
                    mensagens = dados.get("mensagem")
                    respostas = dados.get("resposta") or "Nenhuma mensagem registrada."
                    if dados.get("resposta"):
                        atualizar_visualizada(interaction.user.name,titulo)
                    
                    data_duvida=dados.get("timestamp_duvida")
                    formatted_timestamp = data_duvida.split('.')[0]  # Supondo que timestamp_duvida seja uma string com milissegundos

                    await interaction.user.send(
                        f'----------------------------------------------------'
                        f"\n\n**📝Dúvida Selecionada**\n"
                        f"────────────────────────────────\n\n"
                        f"**Título:** {titulo}\n"
                        f"**Data de Criação:** {formatted_timestamp}\n\n"
                        f"**Mensagens:**\n"
                        f"```{mensagens}```\n\n"
                        f"**Respostas:**\n"
                        f"```{respostas}```\n"
                        )
                await self.load_submenu(interaction)
                return


            if escolha_index < 0 or escolha_index >= len(titulos):
                await interaction.user.send("Escolha inválida. Por favor, escolha um número válido.")
                continue

           
            titulo_escolhido = titulos[escolha_index]
            dados = duvidas.get(titulo_escolhido)

            if dados.get("resposta"):
                atualizar_visualizada(interaction.user.name,titulo_escolhido)

            mensagens = dados.get("mensagem")
            respostas = dados.get("resposta") or "Nenhuma mensagem registrada."
            data_duvida=dados.get("timestamp_duvida")
            formatted_timestamp = data_duvida.split('.')[0]  # Supondo que timestamp_duvida seja uma string com milissegundos

            await interaction.user.send(
                        f"**📝Dúvida Selecionada**\n"
                        f"────────────────────────────────\n\n"
                        f"**Título:** {titulo_escolhido}\n"
                        f"**Data de Criação:** {formatted_timestamp}\n\n"
                        f"**Mensagens:**\n"
                        f"```{mensagens}```\n\n"
                        f"**Respostas:**\n"
                        f"```{respostas}```\n\n"                
                        )


            await self.load_submenu(interaction)
            return

    
    async def show_editar_duvidas(self, interaction: discord.Interaction,user_duvidas):

        user_duvidas = user_duvidas

        if not user_duvidas:
            await interaction.followup.send("Você não tem dúvidas registradas para editar.")
            await  self.load_submenu(interaction)
            return
        
    
        await interaction.followup.send(
            "⚠️ **ATENÇÃO!**\n\n"
            "🛑 **Somente as dúvidas que NÃO foram respondidas podem ser editadas.**\n\n")

        titulos = list(user_duvidas.keys())
        enumeracao = "\n".join([f"{i + 1}. {titulo}" for i, titulo in enumerate(titulos)])
        await interaction.user.send(
            f"Escolha o número de um título para editar uma mensagem associada:\n{enumeracao}"
        )
        

        
        while True:
             
                       
            escolha = await self.gerenciar_timeout(interaction)

            if escolha is None:
                return
            
            escolha=escolha.content.strip()
            
            if not escolha.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue
        
            escolha_index = int(escolha) - 1

            if escolha_index < 0 or escolha_index >= len(titulos):
                await interaction.user.send("Escolha inválida. Tente novamente.")
                continue

            titulo_escolhido = titulos[escolha_index]
            mensagens = user_duvidas[titulo_escolhido]["mensagem"] 
            await interaction.user.send(
                                    f"**📝 Dúvida escolhida com sucesso**\n"
                                    f"────────────────────────────────\n\n"
                                    f"**Título:** {titulo_escolhido}\n" 
                                    f"**Mensagens:**\n"
                                    f"```{mensagens}```\n\n")
            
            await interaction.followup.send("Por favor, digite o novo título da sua dúvida.")
            while  True:

                titulo = await self.gerenciar_timeout(interaction)
                
                if titulo is None:
                    
                    return
                novo_titulo = titulo.content.strip()
                duplicidade_titulo=verificar_duplicidade(interaction.user.name,novo_titulo)
                if duplicidade_titulo:
                    await interaction.user.send(
                    "⚠️ **Aviso:** Você já possui uma dúvida registrada com este título.\n"
                    "Por favor, escolha um título diferente para a sua nova dúvida."
                    )
                else:
                    break


            await interaction.user.send(
            f"✅ **Título alterado com sucesso:** **{novo_titulo}**\n\n"
            "📨 Agora você pode digitar as novas mensagens.\n"
            "✏️ Envie quantas mensagens forem necessárias para explicar sua dúvida.\n\n"
            "🔔 **Quando terminar, digite uma única mensagem com** `enviar` **para encaminhar ao coordenador.**\n\n"
          )

            mensagens=[]
            while True:
                
                nova_msg =  await self.gerenciar_timeout(interaction)
                
                if nova_msg is None:
                    return
                
                nova_msg=nova_msg.content.strip()

                if nova_msg.lower() == "enviar":
                    if len(mensagens)==0:
                        await interaction.user.send('⚠️ Como você não adicionou nenhuma mensagem , sua dúvida não foi alterada!')
                        await  self.load_submenu(interaction) 
                        return 
                    
                    break

                mensagens.append(nova_msg)

            nova_msg_formatadas ="\n".join([f"{msg}" for msg in mensagens]) 

            atualizar_mensagens(interaction.user.name,titulo_escolhido,nova_msg_formatadas,novo_titulo)

            
            await interaction.user.send(
                        f"**📝 Dúvida atualizada com sucesso**\n"
                        f"────────────────────────────────\n\n"
                        f"**Novo título:** {novo_titulo}\n" 
                        f"**Novas Mensagens:**\n"
                        f"```{nova_msg_formatadas}```\n\n"                
                        )

            
            await  self.load_submenu(interaction)
            return

    async def show_deletar_duvidas(self, interaction: discord.Interaction,user_duvidas):
        user_duvidas = user_duvidas

        if not user_duvidas:
            await interaction.followup.send("Você não tem dúvidas registradas para deletar.")
            await  self.load_submenu(interaction)
            return
        
        await interaction.followup.send(
            "⚠️ **ATENÇÃO!**\n\n"
            "🛑 **Somente as dúvidas que NÃO foram respondidas podem ser deletadas.**\n\n"
        )
        
        titulos = list(user_duvidas.keys())
        enumeracao = "\n".join([f"{i + 1}. {titulo}" for i, titulo in enumerate(titulos)])

        await interaction.user.send(
                f"Escolha o número de um título para deletar uma mensagem associada:\n{enumeracao}"
            )

        while True:
            escolha = await self.gerenciar_timeout(interaction)
            
            if escolha is None:
                return

            escolha=escolha.content.strip()

            if not escolha.isdigit():
                await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                continue
        
            escolha_index = int(escolha) - 1

            if escolha_index < 0 or escolha_index >= len(titulos):
                await interaction.user.send("Escolha inválida. Tente novamente.")
                continue
        
            titulo_escolhido = titulos[escolha_index]
            dados = user_duvidas.get(titulo_escolhido)
            mensagens = dados.get("mensagem")
            data_duvida=dados.get("timestamp_duvida")
            formatted_timestamp = data_duvida.split('.')[0]  

            await interaction.user.send(
                        f"**📝 Dúvida Selecionada**\n"
                        f"────────────────────────────────\n\n"
                        f"**Título:** {titulo_escolhido}\n"
                        f"**Data de Criação:** {formatted_timestamp}\n\n"
                        f"**Mensagens:**\n"
                        f"```{mensagens}```\n\n"
                        )
            await interaction.followup.send(
                        f"Tem certeza de que deseja deletar a dúvida?"
                        f"Digite uma opção:\n"
                        f"1️⃣ **Confirmar**\n"
                        f"2️⃣ **Cancelar**")
            
            while True:

                decisao = await self.gerenciar_timeout(interaction)

                if decisao is None:
                    return
                decisao=decisao.content.strip()

                if not decisao.isdigit():
                    await interaction.user.send("Escolha inválida. Por favor, envie um número.")
                    continue
            
                decisao_index = int(decisao)

                if decisao_index not in [1,2]:
                    await interaction.user.send("Escolha inválida. Tente novamente.")
                    continue

                if decisao_index==1:
                    deletar_duvida(interaction.user.name,titulo_escolhido)

                    await interaction.user.send(f"Dúvida **{titulo_escolhido}** excluída com sucesso!")

                elif escolha_index==2:
                    await interaction.user.send(f"Operação cancelada")
                await self.load_submenu(interaction)
                return

async def setup(bot):
    await bot.add_cog(Aluno(bot))