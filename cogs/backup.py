import string

import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import os
import uuid


def generate_backup_id(random_string=10):
    return ''.join(rndm_uuid())

def rndm_uuid():
    rndm = uuid.uuid4().hex[:-8]
    return rndm


def is_admin(user):
    return user.guild_permissions.administrator


class BackupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="backup", description="Backup server data")
    @commands.has_permissions(administrator=True)
    async def backup(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        backup_id = generate_backup_id()


        backup_data = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "channels": [],
            "roles": [],
            "members": [],
        }


        for channel in guild.channels:
            backup_data["channels"].append({
                "name": channel.name,
                "id": channel.id,
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None,
                "position": channel.position,
            })


        for role in guild.roles:
            backup_data["roles"].append({
                "name": role.name,
                "id": role.id,
                "permissions": role.permissions.value,
                "position": role.position,
                "color": role.color.value,
                "mentionable": role.mentionable,
                "hoist": role.hoist,
                "managed": role.managed,
            })


        backup_filename = os.path.join("backups", f"backup_{backup_id}.json")
        os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
        with open(backup_filename, "w") as f:
            json.dump(backup_data, f, indent=4)

        await interaction.followup.send(f"Backup completed successfully! Backup ID: {backup_id}")

    @app_commands.command(name="restore", description="Restore server data from a backup")
    @commands.has_permissions(administrator=True)
    async def restore(self, interaction: discord.Interaction, backup_id: str):
        if not is_admin(interaction.user):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        backup_filename = os.path.join("backups", f"backup_{backup_id}.json")
        if not os.path.exists(backup_filename):
            await interaction.followup.send("Backup not found!")
            return

        with open(backup_filename, "r") as f:
            backup_data = json.load(f)

        guild = interaction.guild


        role_mapping = {}
        for role_data in backup_data["roles"]:
            try:
                role = await guild.create_role(
                    name=role_data["name"],
                    permissions=discord.Permissions(role_data["permissions"]),
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"]
                )
                role_mapping[role_data["id"]] = role.id
            except discord.DiscordException as e:
                await interaction.followup.send(f"Error creating role {role_data['name']}: {e}")
                return


        category_mapping = {}
        for channel_data in backup_data["channels"]:
            try:
                if channel_data["type"] == "category":
                    category = await guild.create_category(name=channel_data["name"], position=channel_data["position"])
                    category_mapping[channel_data["id"]] = category.id
                elif channel_data["type"] == "text":
                    category = guild.get_channel(category_mapping.get(channel_data["category"]))
                    await guild.create_text_channel(name=channel_data["name"], category=category,
                                                    position=channel_data["position"])
                elif channel_data["type"] == "voice":
                    category = guild.get_channel(category_mapping.get(channel_data["category"]))
                    await guild.create_voice_channel(name=channel_data["name"], category=category,
                                                     position=channel_data["position"])
            except discord.DiscordException as e:
                await interaction.followup.send(f"Error creating channel {channel_data['name']}: {e}")
                return

        await interaction.followup.send("Restore completed successfully!")


async def setup(bot):
    await bot.add_cog(BackupCog(bot))