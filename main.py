import discord
from discord.ext import commands
from cfg import token,coll
from vars import bot, extensions, get_prefix
from functions import update_db


@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = f"@Emojifier 4 help. {len(bot.guilds)} Servers"))
    update_db()
    print("Ready Player One.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if len(message.mentions) != 0 and message.mentions[0].id == bot.user.id:
        await message.channel.send(f"Type `{get_prefix(bot, message)}`help for help.")
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    if not coll.find_one({"id": guild.id}):
        coll.insert_one({"name": guild.name, "id": guild.id, "prefix": "&"})

@bot.event
async def on_guild_remove(guild):
    try:
        coll.delete_one({{"id": guild.id}})
    except:
        print("Couldn't find and delete a document")

# loads extensions(cogs) listed in constants.py
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(token)#runs the bot