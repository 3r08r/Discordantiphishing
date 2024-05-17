import discord
import requests
import datetime
import configparser
import re
from discord.ext import commands
from urllib.parse import urlparse

# Load configuration
config = configparser.ConfigParser()
config.read('bot.conf')
TOKEN = config.get('DEFAULT', 'TOKEN')
API_KEY = config.get('DEFAULT', 'API_KEY')
GUILD_ID = int(config.get('DEFAULT', 'GUILD_ID'))
TRACKING_CHANNEL_ID = int(config.get('DEFAULT', 'TRACKING_CHANNEL_ID'))
COLOR = int(config.get('DEFAULT', 'COLOR'), 16)

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',  intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    """Event triggered when a message is received"""
    if message.author == bot.user:
        return

    urls = find_urls_in_message(message.content)
    for url in urls:
        if await is_phishing_link(url):
            await handle_phishing_link(message, url)
            break

    await bot.process_commands(message)

def find_urls_in_message(message):
    """Find URLs in the message"""
    return re.findall(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', message)

async def is_phishing_link(url):
    """Check if a URL is a phishing link using Google Safe Browsing API"""
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}'
    payload = {
        'threatInfo': {
            "threatTypes":      ["THREAT_TYPE_UNSPECIFIED","MALWARE","SOCIAL_ENGINEERING","UNWANTED_SOFTWARE","POTENTIALLY_HARMFUL_APPLICATION"],
            'platformTypes': ["ANY_PLATFORM"],
            'threatEntryTypes': ["URL"],
            'threatEntries': [{'url': url}],
        }
    }

    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'matches' in data:
            return True

    return check_against_links_file(url)

def check_against_links_file(url):
    """Check the URL against a list of known phishing links"""
    url = url.rstrip('/')
    domain = urlparse(url).netloc

    with requests.get('https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt') as response:
        for line in response.iter_lines():
            line = line.decode('utf-8').rstrip('/')
            if domain == line or domain == 'http://' + line or domain == 'https://' + line:
                return True
    return False

async def handle_phishing_link(message, url):
    """Handle the event when a phishing link is detected"""
    await message.delete()
    embed = create_embed(message, url)
    tracking_channel = bot.get_channel(TRACKING_CHANNEL_ID)
    await tracking_channel.send(embed=embed)

def create_embed(message, url):
    """Create an embed message to report the phishing link"""
    embed = discord.Embed(
        title='Phishing Link Detected',
        description=f'A phishing link was detected in a message by {message.author.name}',
        color=discord.Color.red()
    )
    embed.add_field(name='Date', value=datetime.datetime.now().strftime('%Y-%m-%d'))
    embed.add_field(name='Time', value=datetime.datetime.now().strftime('%H:%M:%S'))
    embed.add_field(name='Username', value=message.author.name)
    embed.add_field(name='Message Content', value=message.content)
    return embed

@bot.command(name='whodis')
async def help(ctx):
    """Display help message"""
    embed = discord.Embed(
        title='Phishing Bot',
        description='This bot detects phishing links in messages and reports them to a tracking channel.',
        color=discord.Color.green()
    )
    embed.add_field(name='!whodis', value='Display this message')
    embed.add_field(name='!ping', value='Check if the bot is online')
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is online"""
    await ctx.send('Pong!')
# Run the bot
bot.run(TOKEN)