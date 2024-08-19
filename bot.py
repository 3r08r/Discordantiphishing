import configparser
import discord
import os
from discord.ext import commands


config = configparser.ConfigParser()
config.read("bot.conf")
TOKEN = config.get("DEFAULT", "TOKEN")


intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


bot.config = config
bot.SKIBIDI_KEYWORDS = [
    "skibidi", "skibidi bop", "skibidi bop mm", "skibidi bop mm dada",
    "skibidi dance", "skibidi song", "skibidi meme",
    "skibbidi", "skbidi", "skibi",
    "sk!bidi", "sk*bidi", "sk@bidi", "sk#bidi", "sk$bidi", "sk%bidi", "sk^bidi", "sk&bidi", "sk*bidi", "sk_bidi"
]



async def load_cogs():
    await bot.load_extension("cogs.__init__")



@bot.event
async def on_ready():
    await load_cogs()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="er0r.me"))
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")


bot.run(TOKEN)
