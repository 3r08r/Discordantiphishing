import configparser
import time
import datetime
import json
import re
from urllib.parse import urlparse
import discord
import requests
from discord.ext import commands
#import os
#import google.generativeai as genai


# Load configuration and variables
config = configparser.ConfigParser()
config.read("bot.conf")
TOKEN = config.get("DEFAULT", "TOKEN")
API_KEY = config.get("DEFAULT", "API_KEY")
COLOR = int(config.get("DEFAULT", "COLOR"), 16)
TRACKING_CHANNEL_ID = {}
old_permissions = {}
last_message_time = {}
last_message_content = {}
message_count = {}
timeout_end = {}
IMMUNITY_ROLES = {}
SKIBIDI_KEYWORDS = [
    "skibidi", "skibidi bop", "skibidi bop mm", "skibidi bop mm dada",
    "skibidi dance", "skibidi song", "skibidi meme",
    "skibbidi", "skbidi", "skibi",
    "sk!bidi", "sk\*bidi", "sk\@bidi", "sk\#bidi", "sk\$bidi", "sk%bidi", "sk^bidi", "sk&bidi", "sk\*bidi", "sk\_bidi"
]
SKIBIDI_PATTERN = re.compile(r'\b(?:' + '|'.join(re.escape(keyword) for keyword in SKIBIDI_KEYWORDS) + r')\b', re.IGNORECASE)
# Create a bot instance
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def save_tracking_channel_ids():
    with open("tracking_channel_ids.json", "w") as f:
        json.dump({str(k): v for k, v in TRACKING_CHANNEL_ID.items()}, f)


def load_tracking_channel_ids():
    try:
        with open("tracking_channel_ids.json", "r") as f:
            try:
                TRACKING_CHANNEL_ID.update({int(k): v for k, v in json.load(f).items()})
            except json.JSONDecodeError:
                pass  # It's okay if the file is not valid JSON
    except FileNotFoundError:
        pass  # It's okay if the file doesn't exist
def load_immunity_roles():
    try:
        with open("immunity_roles.json", "r") as f:
            IMMUNITY_ROLES.update(json.load(f))
    except FileNotFoundError:
        pass

def save_immunity_roles():
    with open("immunity_roles.json", "w") as f:
        json.dump(IMMUNITY_ROLES, f)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="er0r.me"))
    await bot.tree.sync()
    """Event triggered when the bot is ready"""
    print(f"Logged in as {bot.user.name}")
    load_tracking_channel_ids()

@bot.event
async def on_message(message):
        """Event triggered when a message is received"""
        if message.author == bot.user:
            return

        # Check if the user is currently timed out
        if message.author.id in timeout_end and time.time() < timeout_end[message.author.id]:
            await message.delete()
            return

        if any(role.id in IMMUNITY_ROLES.get(message.guild.id, []) for role in message.author.roles) or message.author.guild_permissions.administrator:
            return

        # Get the current time
        current_time = time.time()

        # Check if the user has sent a message in the last 2 seconds
        if message.author.id in last_message_time and current_time - last_message_time[message.author.id] < 2:
            # If they have, increment their message count
            message_count[message.author.id] = message_count.get(message.author.id, 0) + 1

            # If they've sent more than 3 messages in the last 2 seconds, time them out for 10 seconds
            if message_count[message.author.id] > 4:
                timeout_end[message.author.id] = time.time() + 20
            else:
                # If they haven't, update the timestamp
                last_message_time[message.author.id] = current_time
        else:
            # If they haven't sent a message in the last 2 seconds, reset their message count
            message_count[message.author.id] = 1
            last_message_time[message.author.id] = current_time

    # Check if the user has sent the same message as the last one
        if message.author.id in last_message_content and message.content == last_message_content[message.author.id]:
            await message.delete()
            try:
                await message.author.send(f"{message.author.mention}, please do not repeat the same message.")
            except discord.errors.Forbidden:
                print(f"Unable to send DM to {message.author.mention}")
        else:
            # If it's not the same, update the last message
            last_message_content[message.author.id] = message.content

        # Check if the message mentions more than 5 users
        if len(message.mentions) > 5:
            await message.delete()
            try:
                await message.author.send(f"{message.author.mention}, please do not mention too many users.")
            except discord.errors.Forbidden:
                print(f"Unable to send DM to {message.author.mention}")

        # Check if the message contains more than 3 URLs
        urls = re.findall(r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+", message.content)
        if len(urls) > 3:
            await message.delete()
            try:
                await message.author.send(f"{message.author.mention}, please do not send too many links.")
            except discord.errors.Forbidden:
                print(f"Unable to send DM to {message.author.mention}")

        await bot.process_commands(message)
        # anti phishing
        urls = find_urls_in_message(message.content)
        for url in urls:
            if await is_phishing_link(url):
                await handle_phishing_link(message, url)
                break

        await bot.process_commands(message)


def find_urls_in_message(message):
    """Find URLs in the message"""
    return re.findall(r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+", message)


async def is_phishing_link(url):
    """Check if a URL is a phishing link using Google Safe Browsing API"""
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    payload = {
        "threatInfo": {
            "threatTypes": [
                "THREAT_TYPE_UNSPECIFIED",
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        }
    }

    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if "matches" in data:
            return True

    return check_against_links_file(url)


def check_against_links_file(url):
    """Check the URL against a list of known phishing links"""
    url = url.rstrip("/")
    domain = urlparse(url).netloc

    with requests.get(
            "https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt"
    ) as response:
        for line in response.iter_lines():
            line = line.decode("utf-8").rstrip("/")
            if (
                    domain == line
                    or domain == "http://" + line
                    or domain == "https://" + line
            ):
                return True
    return False


async def handle_phishing_link(message, url):
    """Handle the event when a phishing link is detected"""
    await message.delete()
    embed = create_embed(message, url)
    tracking_channel_id = TRACKING_CHANNEL_ID.get(message.guild.id)
    if tracking_channel_id is not None:
        tracking_channel = bot.get_channel(tracking_channel_id)
        await tracking_channel.send(embed=embed)
    else:
        print(f"No tracking channel set for guild {message.guild.id}")


def create_embed(message, url):
    """Create an embed message to report the phishing link"""
    embed = discord.Embed(
        title="Phishing Link Detected",
        description=f"A phishing link was detected in a message by {message.author.name}",
        color=discord.Color.red(),
    )
    embed.add_field(name="Date", value=datetime.datetime.now().strftime("%Y-%m-%d"))
    embed.add_field(name="Time", value=datetime.datetime.now().strftime("%H:%M:%S"))
    embed.add_field(name="Username", value=message.author.name)
    embed.add_field(name="Message Content", value=message.content)
    embed.add_field(name="Phishing URL", value=url)
    return embed


@bot.hybrid_command(name="whodis")
async def help(ctx):
    """Display help message"""
    embed = discord.Embed(
        title="Phishing Bot",
        description="This bot detects phishing links in messages and reports them to a tracking channel.",
        color=discord.Color.green(),
    )
    embed.add_field(name="/whodis", value="Display this message")
    embed.add_field(name="/ping", value="Check if the bot is online")
    embed.add_field(
        name="/set_tracking_channel <channel>",
        value="Set the tracking channel for the server",
    )
    embed.add_field(name="/lock_channel", value="Lock the channel for the server")
    embed.add_field(name="/unlock_channel", value="Unlock the channel for the server")
    await ctx.send(embed=embed)


@bot.hybrid_command(name="ping")
async def ping(ctx):
    """Check if the bot is online"""
    await ctx.send("Pong!")


@bot.hybrid_command(name="set_tracking_channel")
@commands.has_permissions(administrator=True)
async def set_tracking_channel(ctx, channel: discord.TextChannel):
    """Set the tracking channel for the server"""
    TRACKING_CHANNEL_ID[ctx.guild.id] = channel.id
    await ctx.send(f"Tracking channel has been set to {channel.name}")
    save_tracking_channel_ids()


@bot.hybrid_command(name="lock_channel")
@commands.has_permissions(administrator=True)
async def lock_channel(ctx):
    """Lock the channel for the server"""
    # Store the old permissions and deny send_messages permission for every role
    for role in ctx.guild.roles:
        old_permissions[role.id] = ctx.channel.overwrites_for(role)
        await ctx.channel.set_permissions(role, send_messages=False)
    await ctx.send(f"Channel has been locked")


@bot.hybrid_command(name="unlock_channel")
@commands.has_permissions(administrator=True)
async def unlock_channel(ctx):
    """Unlock the channel for the server"""
    # Restore the old permissions for every role
    for role in ctx.guild.roles:
        await ctx.channel.set_permissions(role, overwrite=old_permissions.get(role.id))
    await ctx.send(f"Channel has been unlocked")




@bot.event
async def on_command_error(ctx, error):
    """Event triggered when a command raises an error"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I didn't recognize that command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing some required arguments.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")
    else:
        await ctx.send("An error occurred while processing the command.")



@bot.event
async def on_message(message):
    """Event triggered when a message is received"""
    if message.author == bot.user:
        return
    if any(role.id in IMMUNITY_ROLES.get(message.guild.id, []) for role in message.author.roles) or message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    # Check if the message contains any skibidi keywords using regex
    if SKIBIDI_PATTERN.search(message.content):
        await message.delete()
        # Create an embed message with details about the deleted message
        embed = discord.Embed(
            title="Message Deleted",
            description=f"A message containing 'skibidi' keywords was deleted.",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=message.author.name, inline=True)
        embed.add_field(name="Channel", value=message.channel.name, inline=True)
        embed.add_field(name="Message Content", value=message.content, inline=False)
        embed.add_field(name="Date", value=datetime.datetime.now().strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Time", value=datetime.datetime.now().strftime("%H:%M:%S"), inline=True)

        # Send the embed message to the tracking channel
        tracking_channel_id = TRACKING_CHANNEL_ID.get(message.guild.id)
        if tracking_channel_id is not None:
            tracking_channel = bot.get_channel(tracking_channel_id)
            await tracking_channel.send(embed=embed)
        else:
            print(f"No tracking channel set for guild {message.guild.id}")

        return

    # Check if the user is currently timed out
    if message.author.id in timeout_end and time.time() < timeout_end[message.author.id]:
        await message.delete()
        return

    # Get the current time
    current_time = time.time()
    await bot.process_commands(message)

@bot.hybrid_command(name="add_immunity_role")
@commands.has_permissions(administrator=True)
async def add_immunity_role(ctx, role: discord.Role):
        """Add a role to the immunity list"""
        if ctx.guild.id not in IMMUNITY_ROLES:
            IMMUNITY_ROLES[ctx.guild.id] = []
        if role.id not in IMMUNITY_ROLES[ctx.guild.id]:
            IMMUNITY_ROLES[ctx.guild.id].append(role.id)
            save_immunity_roles()
            await ctx.send(f"Role {role.name} has been added to the immunity list.")
        else:
            await ctx.send(f"Role {role.name} is already in the immunity list.")

@bot.hybrid_command(name="remove_immunity_role")
@commands.has_permissions(administrator=True)
async def remove_immunity_role(ctx, role: discord.Role):
        """Remove a role from the immunity list"""
        if ctx.guild.id in IMMUNITY_ROLES and role.id in IMMUNITY_ROLES[ctx.guild.id]:
            IMMUNITY_ROLES[ctx.guild.id].remove(role.id)
            save_immunity_roles()
            await ctx.send(f"Role {role.name} has been removed from the immunity list.")
        else:
            await ctx.send(f"Role {role.name} is not in the immunity list.")

    # Run the bot
bot.run(TOKEN)
