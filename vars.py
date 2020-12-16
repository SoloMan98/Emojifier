from discord.ext import commands
from cfg import coll

#Cogs the bot loads
extensions = ["cogs.commands",
              "cogs.emoji",
              "cogs.error_handler"]

prefix = "tmp"

def get_prefix(bot, message):
    try:  
        return coll.find_one({"id": message.guild.id})["prefix"]
    except:
        return "&"

bot = commands.Bot(command_prefix = get_prefix, help_command = None) #creates bot

help_dict ={
            f"{prefix}howdy":f"We all need friends",  
            f"{prefix}resize <target size>":f"This command will resize an attached image to be just under a specified size in bytes",
            f"{prefix}this <name>":f"This command will automatically resize an emoji and add it to the guild under an optional name",
            f"{prefix}above <name>":f"This command will look 5 messages deep into channel history and emojify that image",
            }

error_dict = {
    101: "Please attach an image with the command",
    102: "This image is already well sized",
    103: "This image is too large",
    104: "Image is not of supported file types (PNG, JPG, GIF)"
}

change_log = {
    "0.6": {
        "Default Command Changed": "Changed default command from 'emojify ' to '&'",
        "Added Server Prefixes": "Users can change prefix with &prefix command",
        "Database usage": "Data for server prefixes now stored in cloud",
        "@mention the bot": "@emojifier now shows the prefix and help command"
    },
    "0.5": {
        "Resize Above Images": "Users can '&emojify above' and add the above pictures without having to send all in one msg",
        "New algorithm": "Uses a new algorithm that isnt linear to increase accuracy without drop in performance"
    }
}