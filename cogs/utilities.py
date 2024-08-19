import json
import discord
from discord.ext import commands
from .base_cog import BaseCog


class utilities(BaseCog):

    def save_tracking_channel_ids(self):
        with open("tracking_channel_ids.json", "w") as f:
            json.dump({str(k): v for k, v in self.tracking_channel_ids.items()}, f)

    def save_immunity_roles(self):
        with open("immunity_roles.json", "w") as f:
            json.dump(self.immunity_roles, f)

    def load_immunity_roles(self):
        try:
            with open("immunity_roles.json", "r") as f:
                self.immunity_roles.update(json.load(f))
        except FileNotFoundError:
            pass

    @commands.hybrid_command(name="set_tracking_channel")
    @commands.has_permissions(administrator=True)
    async def set_tracking_channel(self, ctx, channel: discord.TextChannel):
        self.tracking_channel_ids[ctx.guild.id] = channel.id
        await ctx.send(f"Tracking channel has been set to {channel.name}")
        self.save_tracking_channel_ids()

    @commands.hybrid_command(name="add_immunity_role")
    @commands.has_permissions(administrator=True)
    async def add_immunity_role(self, ctx, role: discord.Role):
        if ctx.guild.id not in self.immunity_roles:
            self.immunity_roles[ctx.guild.id] = []
        if role.id not in self.immunity_roles[ctx.guild.id]:
            self.immunity_roles[ctx.guild.id].append(role.id)
            self.save_immunity_roles()
            await ctx.send(f"Role {role.name} has been added to the immunity list.")
        else:
            await ctx.send(f"Role {role.name} is already in the immunity list.")

    @commands.hybrid_command(name="remove_immunity_role")
    @commands.has_permissions(administrator=True)
    async def remove_immunity_role(self, ctx, role: discord.Role):
        if ctx.guild.id in self.immunity_roles and role.id in self.immunity_roles[ctx.guild.id]:
            self.immunity_roles[ctx.guild.id].remove(role.id)
            self.save_immunity_roles()
            await ctx.send(f"Role {role.name} has been removed from the immunity list.")
        else:
            await ctx.send(f"Role {role.name} is not in the immunity list.")

    @commands.hybrid_command(name="lock_channel")
    @commands.has_permissions(administrator=True)
    async def lock_channel(self, ctx):
        for role in ctx.guild.roles:
            await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send(f"Channel has been locked")

    @commands.hybrid_command(name="unlock_channel")
    @commands.has_permissions(administrator=True)
    async def unlock_channel(self, ctx):
        for role in ctx.guild.roles:
            await ctx.channel.set_permissions(role, send_messages=None)
        await ctx.send(f"Channel has been unlocked")


async def setup(bot):
    await bot.add_cog(utilities(bot))
