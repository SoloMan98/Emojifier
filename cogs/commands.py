import discord
from discord.ext import commands
import vars
from vars import bot
from cfg import coll

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'howdy')
    async def howdy(self, ctx):
        await ctx.channel.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command()
    async def help(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        #generate formatted embed to send to user
        help_embed = discord.Embed(title = "🙌🏻General Commands🙌🏻", description = " ", color = discord.Colour.blue())
        for k,v in list(vars.help_dict.items()):
            help_embed.add_field(name = k, value = v, inline=False)
        
        await ctx.message.author.send(embed = help_embed)#send message to user

    @commands.command()
    async def write(self, ctx, content):
        await ctx.send(content)

    @commands.command(name = "prefix")
    async def change_prefix(self, ctx, new_prefix = None):
        if not new_prefix:
            return await ctx.send("You must provide a new prefix Ex.(&prefix $)")

        coll.find_one_and_update(
            {"id": ctx.guild.id},
            {'$set' : {"prefix": new_prefix}}
        )

        return await ctx.send(f"Successfully Changed prefix to `{new_prefix}`")
        
    @commands.command(name = "patchnotes")
    async def patchnotes(self, ctx, version = None):
        #generate formatted embed to send to user
        latest = "0.6"

        #get correct version
        if version in vars.change_log.keys():
            info = vars.change_log[version]
        else:
            info = vars.change_log[latest]
            version = latest

        #create and add to embed
        patch_embed = discord.Embed(title = f"Emojifier v{version} Patch Notes",
                                    description = f"Current Version: {latest}\n Versions: {', '.join(vars.change_log.keys())}", 
                                    color = discord.Colour.blue())
        for k,v in info.items():
            patch_embed.add_field(name = k, value = v)

        return await ctx.send(embed = patch_embed)

def setup(bot):
    bot.add_cog(BaseCommands(bot))