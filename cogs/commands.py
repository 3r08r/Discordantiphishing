import discord
from discord.ext import commands
from .base_cog import BaseCog

class BotCommands(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.original_permissions = {}
    @commands.hybrid_command(name="sigma")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Phishing Bot",
            description="This bot detects phishing links in messages and reports them to a tracking channel.",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="/whodis",
            value="Display this message"
        )
        embed.add_field(
            name="/ping",
            value="Check if the bot is online"
        )
        embed.add_field(
            name="/set_tracking_channel <channel>",
            value="Set the tracking channel for the server",
        )
        embed.add_field(
            name="/lock_channel",
            value="Lock the channel for the server"
        )
        embed.add_field(
            name="/unlock_channel",
            value="Unlock the channel for the server"
        )
        embed.add_field(
            name="/add_immunity_role <role>",
            value="Add a role to the immunity list",
        )
        embed.add_field(
            name="/remove_immunity_role <role>",
            value="Remove a role from the immunity list",
        )
        embed.add_field(
            name="/backup",
            value="Backup server data",
        )
        embed.add_field(
            name="/restore <backup_id>",
            value="Restore server data from a backup",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping")
    async def cmd_ping(self, ctx):
        await ctx.send("Pong!")
# Set Tracking Channel fixed , saved in die datei via add_tracking_channel_id
    @commands.hybrid_command(name="set_tracking", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def cmd_set_tracking_channel(self, ctx, channel: discord.TextChannel):

        try:
            await self.add_tracking_channel_id(ctx.guild.id, channel.id)
            await ctx.send(f"Tracking channel has been set to {channel.mention}")

        except Exception as e:
            await ctx.send(f"An error occurred while processing the command: {e}")

    @commands.hybrid_command(name="add_immunity_role")
    @commands.has_permissions(administrator=True)
    async def cmd_add_immunity_role(self, ctx, role: discord.Role):
        guild_id = ctx.guild.id
        role_id = role.id
        await self.add_immunity_role(guild_id, role_id)
        await ctx.send(f"Role {role.name} ist nun immun.")
    @commands.hybrid_command(name="remove_immunity_role")
    @commands.has_permissions(administrator=True)
    async def cmd_remove_immunity_role(self, ctx, role: discord.Role):
        await self.remove_immunity_role(ctx.guild.id, role.id)
        await ctx.send(f"Role {role.name} ist nicht mehr immun.")

    @commands.hybrid_command(name="is_immune")
    async def cmd_is_immune(self, ctx, role: discord.Role):
        is_immune = await self.has_immunity_role(ctx.guild.id, role.id)
        if is_immune == True:
            await ctx.send(f"Role {role.name} ist immun.")
        else:
            await ctx.send(f"Role {role.name} ist nicht immun.")


    @commands.hybrid_command(name="lock_channel")
    @commands.has_permissions(administrator=True)
    async def cmd_lock_channel(self, ctx):
        self.original_permissions[ctx.channel.id] = {}
        for role in ctx.guild.roles:
            self.original_permissions[ctx.channel.id][role.id] = ctx.channel.overwrites_for(role).send_messages
            await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send("Channel has been locked")

    @commands.hybrid_command(name="unlock_channel")
    @commands.has_permissions(administrator=True)
    async def cmd_unlock_channel(self, ctx):
        if ctx.channel.id in self.original_permissions:
            for role in ctx.guild.roles:
                original_send_messages = self.original_permissions[ctx.channel.id].get(role.id, None)
                await ctx.channel.set_permissions(role, send_messages=original_send_messages)
            await ctx.send("Channel has been unlocked")
        else:
            await ctx.send("No original permissions found for this channel")




async def setup(bot):
    await bot.add_cog(BotCommands(bot))