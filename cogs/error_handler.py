import discord
from discord.ext import commands
from vars import bot

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(f'error: {error}')
        #more info @ https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        error_embed = discord.Embed(title = f'Your command: {ctx.message.content}',
                                    description = f"You goofed. This is why: {error}",
                                    color = discord.Colour.red())
        await ctx.send(embed = error_embed, delete_after = 30)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
