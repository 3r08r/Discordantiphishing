import json
import datetime
import discord
from discord.ext import commands
from .base_cog import BaseCog


class utilities(BaseCog):



    def save_immunity_roles(self):
        with open("immunity_roles.json", "w") as f:
            json.dump(self.immunity_roles, f)

    def load_immunity_roles(self):
        try:
            with open("immunity_roles.json", "r") as f:
                self.immunity_roles.update(json.load(f))
        except FileNotFoundError:
            pass

async def setup(bot):
    await bot.add_cog(utilities(bot))
