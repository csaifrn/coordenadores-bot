from discord.ext import commands
import discord

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        lista = ['palavrão', 'burro']

        if any(palavra.lower() in message.content.lower() for palavra in lista):
            await message.channel.send(
                f"Mensagem do {message.author.name} no canal {message.channel.name} foi deletada por violar as diretrizes do canal"
            )
            await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, membro: discord.Member):
        canal = self.bot.get_channel(1317165412739186720)
        if canal is not None:
            meu_embed = discord.Embed(title=f'Bem-vindo, {membro.name}!', description='Aproveite a estadia!')
            meu_embed.set_thumbnail(url=membro.avatar.url)  

            await canal.send(embed=meu_embed)

async def setup(bot):
    await bot.add_cog(Manager(bot))
