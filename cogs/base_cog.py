import discord
import json
from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracking_channel_ids = {}
        self.immunity_roles = {}
        self.load_tracking_channel_ids()

    def load_tracking_channel_ids(self):
        try:
            with open("tracking_channel_ids.json", "r") as f:
                try:
                    self.tracking_channel_ids.update({int(k): v for k, v in json.load(f).items()})
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass


async def setup(bot):
    pass
