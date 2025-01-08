from discord.ext import commands
import discord
from discord import app_commands
import asyncio

from Commands.aluno import duvidas_por_usuario  # Importa o dicionário compartilhado com as dúvidas

class Coordenador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(description="Visualizar títulos de dúvidas não respondidas e responder.")
    async def fila_duvidas(self, interaction: discord.Interaction):

      
       
        # Filtra apenas as dúvidas que não foram respondidas
        duvidas_nao_respondidas = [
            {"usuario_id": uid, "titulo": titulo}
            for uid, duvidas in duvidas_por_usuario.items()
            for titulo, dados in duvidas.items()
            if not dados.get("respostas")  # Verifica se o campo 'respostas' está vazio
        ]

        
        
        if not duvidas_nao_respondidas:
            await interaction.response.send_message("Nenhuma dúvida não respondida no momento.")
            return

        lista_titulos = "\n".join([f"{i + 1}. {item['titulo']}" for i, item in enumerate(duvidas_nao_respondidas)])
        await interaction.response.send_message(
            f"Selecione um título pela posição na lista para visualizar as mensagens:\n{lista_titulos}"
        )

    
        # Escolha do título
        escolha_titulo = await self.bot.wait_for(
            'message'
        )
        escolha_index = int(escolha_titulo.content) - 1

        if escolha_index < 0 or escolha_index >= len(duvidas_nao_respondidas):
            await interaction.followup.send("Escolha inválida. Por favor, tente novamente.")
            return

        titulo_selecionado = duvidas_nao_respondidas[escolha_index]
        usuario_id = titulo_selecionado["usuario_id"]
        titulo = titulo_selecionado["titulo"]
        dados = duvidas_por_usuario[usuario_id][titulo]

        mensagens = dados.get("mensagens", [])
        mensagens_formatadas = "\n".join([f"- {msg}" for msg in mensagens]) if mensagens else "Nenhuma mensagem registrada."

        await interaction.followup.send(
            f"**{titulo}**\n"
            f"**Mensagens:**\n{mensagens_formatadas}\n"
            "Agora você pode responder a essa dúvida. Envie suas respostas.\n"
            "Digite 'finalizar' para encerrar."
        )

        # Coletar múltiplas respostas
        respostas = []
        while True:
            resposta_msg = await self.bot.wait_for(
                'message'
            )
            resposta = resposta_msg.content

            if resposta.lower() == 'parar':
                break
            
            respostas.append(resposta)

        # Adicionar respostas ao título
        dados["respostas"].extend(respostas)
        await interaction.followup.send(
            f"Respostas adicionadas ao título **{titulo}**:\n"
            f"{chr(10).join([f'- {r}' for r in respostas])}\n"
            "O título foi atualizado com as novas respostas."
        )


     
async def setup(bot):
    await bot.add_cog(Coordenador(bot))
