from discord.ext import commands
import discord
import asyncio
from discord import app_commands

duvidas_por_usuario = {}


class Aluno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.atendimento_ativo = {}

    @app_commands.command(description='Inicia o atendimento e captura as mensagens com um título definido pelo usuário.')
    async def iniciar_atendimento(self, interaction: discord.Interaction):
        if interaction.user.id in self.atendimento_ativo:
            await interaction.response.send_message("Você já está em um atendimento.")
            return

        await interaction.response.send_message("Por favor, digite o título da sua dúvida.")

       
        titulo_msg = await self.bot.wait_for('message')
        titulo = titulo_msg.content.strip()
        

        self.atendimento_ativo[interaction.user.id] = titulo
        if interaction.user.id not in duvidas_por_usuario:
            duvidas_por_usuario[interaction.user.id] = {}
        duvidas_por_usuario[interaction.user.id][titulo] = {"mensagens": [], "respostas": []}

        await interaction.followup.send(
            f"Título registrado: **{titulo}**. Agora você pode digitar as mensagens da sua dúvida. "
            "Envie 'parar' ou use o comando '/finalizar_atendimento' para encerrar."
        )

        while True:
            mensagem = await self.bot.wait_for('message')

            if mensagem.content.lower() == "parar":
                await self.finalizar_atendimento(interaction)  
                break
                

            duvidas_por_usuario[interaction.user.id][titulo]["mensagens"].append(mensagem.content)

    async def finalizar_atendimento(self, interaction: discord.Interaction):
       
        titulo = self.atendimento_ativo.pop(interaction.user.id, None)
        mensagens = duvidas_por_usuario.get(interaction.user.id, {}).get(titulo, {}).get("mensagens", [])

        if mensagens:
            mensagem_resumo = "\n".join([f"- {m}" for m in mensagens])
            await interaction.followup.send(
                f"Atendimento encerrado. Dúvida registrada com o título **{titulo}**:\n{mensagem_resumo}"
            )
        else:
            await interaction.followup.send("Nenhuma mensagem foi registrada durante o atendimento.")

    @app_commands.command(description='Conferir dúvidas registradas.')
    async def conferir_atendimento(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_duvidas = duvidas_por_usuario.get(user_id)

        if not user_duvidas:
            await interaction.response.send_message("Você não possui dúvidas registradas.")
            return

        titulos = list(user_duvidas.keys())
        enumeracao = "\n".join([f"{i + 1}. {titulo}" for i, titulo in enumerate(titulos)])

        await interaction.response.send_message(
            f"Escolha o número de um título para visualizar as mensagens e respostas associadas:\n{enumeracao}"
        )


        escolha = await self.bot.wait_for('message')
        escolha_index = int(escolha.content) - 1

        if escolha_index < 0 or escolha_index >= len(titulos):
            await interaction.followup.send("Escolha inválida. Por favor, tente novamente.")
            return

        titulo_escolhido = titulos[escolha_index]
        dados = user_duvidas.get(titulo_escolhido, {})
        mensagens = dados.get("mensagens", [])
        respostas = dados.get("respostas", [])

        mensagens_formatadas = "\n".join([f"- {msg}" for msg in mensagens]) if mensagens else "Nenhuma mensagem registrada."
        respostas_formatadas = "\n".join([f"- {resp}" for resp in respostas]) if respostas else "Nenhuma resposta registrada."

        await interaction.followup.send(
            f"**{titulo_escolhido}**\n"
            f"**Mensagens:**\n{mensagens_formatadas}\n\n"
            f"**Respostas:**\n{respostas_formatadas}"
        )

async def setup(bot):
    await bot.add_cog(Aluno(bot))
