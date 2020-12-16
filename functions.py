from cfg import coll
from vars import bot

def update_db():
    #search all guilds for a document
    for guild in bot.guilds:
        if not coll.find_one({"id": guild.id}):
            coll.insert_one({"name": guild.name, "id": guild.id, "prefix": "&"})

def clean_db():
    data = list(coll.find())
    if len(data) == 0:
        return

    #look for documents that are hidden
    for doc in data:
        if doc["id"] not in [guild.id for guild in bot.guilds]:
            coll.delete_one(doc)