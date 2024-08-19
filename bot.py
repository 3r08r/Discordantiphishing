import configparser
import discord
import os
from discord.ext import commands

# Load configuration and variables
config = configparser.ConfigParser()
config.read("bot.conf")
TOKEN = config.get("DEFAULT", "TOKEN")

# Create a bot instance
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Add config and keywords as attributes of bot
bot.config = config
bot.SKIBIDI_KEYWORDS = [
    "skibidi", "skibidi bop", "skibidi bop mm", "skibidi bop mm dada",
    "skibidi dance", "skibidi song", "skibidi meme",
    "skibbidi", "skbidi", "skibi",
    "sk!bidi", "sk*bidi", "sk@bidi", "sk#bidi", "sk$bidi", "sk%bidi", "sk^bidi", "sk&bidi", "sk*bidi", "sk_bidi"
]


# Load cogs
async def load_cogs():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


# Run the bot
@bot.event
async def on_ready():
    await load_cogs()


bot.run(TOKEN)
