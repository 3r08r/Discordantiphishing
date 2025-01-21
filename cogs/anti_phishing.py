import re
import asyncio
import aiohttp
from urllib.parse import urlparse
from discord.ext import commands
from .base_cog import BaseCog
from .events import BotEvents
from urlextract import URLExtract


class AntiPhishing(BotEvents, BaseCog):

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
        

 

        try:
            # Handle skibidi keyword messages
            if self.SKIBIDI_PATTERN.search(message.content):
                await self.handle_skibidi_message(message)

            # Check if the message contains phishing URLs
            urls = self.find_urls_in_message(message.content)
            for url in urls:
                if await self.is_phishing_link(url):
                    await self.handle_phishing_link(message, url)
                    break
        except Exception as e:
            print(f"no skibidi or phishing link found: {e}")

    def find_urls_in_message(self, message):
        extractor = URLExtract()
        urls = extractor.find_urls(message)
        return urls

    async def is_phishing_link(self, url):
        api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.API_KEY}"
        payload = {
            "threatInfo": {
                "threatTypes": ["SOCIAL_ENGINEERING", "MALWARE", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "matches" in data:
                            return True
                    else:
                        print(f"Error: Google Safe Browsing API returned status {response.status}")
        except aiohttp.ClientError as e:
            print(f"Error contacting Google Safe Browsing API: {e}")
        except asyncio.TimeoutError:
            print("Error: Request to Google Safe Browsing API timed out.")

        return False

    async def check_against_links_file(self, url):
        domain = urlparse(url).netloc.rstrip("/")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt",
                        timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        if domain in content:
                            return True
                    else:
                        print(f"Error: Phishing URL list returned status {response.status}")
        except aiohttp.ClientError as e:
            print(f"Error fetching phishing URL list: {e}")
        except asyncio.TimeoutError:
            print("Error: Request to fetch phishing URL list timed out.")

        return False


async def setup(bot):
    await bot.add_cog(AntiPhishing(bot))