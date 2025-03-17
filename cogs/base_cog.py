import discord
import json
from discord.ext import commands
import json
import os


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#Funktioniert, added zeile in json datei
    async def add_tracking_channel_id(cls, guild_id, channel_id):
        data = {}
        try:
            with open("tracking_channel_ids.json", "r") as f:
                    data = json.load(f)
        except FileNotFoundError:
            data = {}
        tracking_channel = {

            "guild_id": guild_id,
            "channel_id": channel_id

        }
        data[guild_id] = tracking_channel


        with open("tracking_channel_ids.json", "w") as f:
            json.dump(data, f)


    @classmethod
    async def get_tracking_channel_id(cls, guild_id):
        try:
            with open("tracking_channel_ids.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        if not data:
            return None

        for gid, details in data.items():
            if gid == str(guild_id):
                return details.get("channel_id")

        return None



    async def add_immunity_role(cls, guild_id, role_id):
        data = {}
        try:
            with open("immunity_roles.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        if str(guild_id) not in data:
            data[str(guild_id)] = []

        if str(role_id) not in data[str(guild_id)]:
            data[str(guild_id)].append(str(role_id))

        with open("immunity_roles.json", "w") as f:
            json.dump(data, f)
        return True

    @classmethod
    async def has_immunity_role(cls, guild_id, role_id):
        try:
            with open("immunity_roles.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return False
        
        if str(role_id) in data.get(str(guild_id), []):
            return True
        else:
            return False 
    
    async def remove_immunity_role(cls, guild_id, role_id):
        try:
            with open("immunity_roles.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return

        if str(guild_id) in data and str(role_id) in data[str(guild_id)]:
            data[str(guild_id)].remove(str(role_id))

            with open("immunity_roles.json", "w") as f:
                json.dump(data, f)
    


async def setup(bot):
    pass
