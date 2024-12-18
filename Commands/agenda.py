from discord.ext import commands
import discord
from discord import app_commands

class ChecklistView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.tarefas = {
            "1. Configurar o ambiente": False,
            "2. Escrever o código": False,
            "3. Testar funcionalidades": False,
            "4. Revisar o código": False,
            "5. Publicar no servidor": False
        }
        for tarefa in self.tarefas.keys():
            self.add_item(CheckButton(tarefa, self))

        self.add_item(SendButton(self))

class CheckButton(discord.ui.Button):
    def __init__(self, tarefa: str, parent_view: ChecklistView):
        super().__init__(label=f"🔲 {tarefa}", style=discord.ButtonStyle.secondary)
        self.tarefa = tarefa
        self.parent_view = parent_view 
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.tarefas[self.tarefa] = not self.parent_view.tarefas[self.tarefa]

        self.label = f"{'✅' if self.parent_view.tarefas[self.tarefa] else '🔲'} {self.tarefa}"
        await interaction.response.edit_message(view=self.parent_view)

class SendButton(discord.ui.Button):
    def __init__(self, parent_view: ChecklistView):
        super().__init__(label="Enviar", style=discord.ButtonStyle.green)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        concluidas = [tarefa for tarefa, marcada in self.parent_view.tarefas.items() if marcada]

        if concluidas:
            await interaction.response.send_message(
                f"Tarefas enviadas:\n- " + "\n- ".join(concluidas),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Nenhuma tarefa selecionada. Por favor, marque pelo menos uma.",
                ephemeral=True
            )

class AgendaView(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='Checklist')
    async def checklist(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Checklist de Tarefas:",
            view=ChecklistView()
        )

async def setup(bot):
    await bot.add_cog(AgendaView(bot))
