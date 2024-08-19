import re
import requests
import discord
import datetime
from urllib.parse import urlparse
from discord.ext import commands
from .base_cog import BaseCog


class AntiPhishing(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)

    def load_tracking_channel_ids(self):
        try:
            with open("tracking_channel_ids.json", "r") as f:
                try:
                    self.tracking_channel_ids.update({int(k): v for k, v in json.load(f).items()})
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass

    def __init__(self, bot):
        self.bot = bot
        self.tracking_channel_ids = {}
        self.API_KEY = self.bot.config.get("DEFAULT", "API_KEY")
        self.SKIBIDI_PATTERN = re.compile(
            r'\b(?:' + '|'.join(re.escape(keyword) for keyword in self.bot.SKIBIDI_KEYWORDS) + r')\b', re.IGNORECASE)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Handle skibidi keyword messages
        if self.SKIBIDI_PATTERN.search(message.content):
            await self.handle_skibidi_message(message)

        # Check if the message contains phishing URLs
        urls = self.find_urls_in_message(message.content)
        for url in urls:
            if await self.is_phishing_link(url):
                await self.handle_phishing_link(message, url)
                break

    def find_urls_in_message(self, message):
        return re.findall(r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+", message)

    async def is_phishing_link(self, url):
        api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.API_KEY}"
        payload = {
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            }
        }
        response = requests.post(api_url, json=payload)
        if response.status_code == 200 and "matches" in response.json():
            return True
        return self.check_against_links_file(url)

    def check_against_links_file(self, url):
        domain = urlparse(url).netloc.rstrip("/")
        response = requests.get("https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt")
        for line in response.iter_lines():
            if domain in line.decode("utf-8"):
                return True
        return False

    async def handle_phishing_link(self, message, url):
        await message.delete()
        embed = self.create_embed(message, url)
        tracking_channel_id = self.tracking_channel_ids.get(message.guild.id)
        if tracking_channel_id:
            tracking_channel = self.bot.get_channel(tracking_channel_id)
            await tracking_channel.send(embed=embed)

    def create_embed(self, message, url):
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

    async def handle_skibidi_message(self, message):
        await message.delete()
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
        tracking_channel_id = self.tracking_channel_ids.get(message.guild.id)
        if tracking_channel_id:
            tracking_channel = self.bot.get_channel(tracking_channel_id)
            await tracking_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AntiPhishing(bot))
