import datetime
import discord
import json
from discord.ext import commands
from .base_cog import BaseCog


class BotEvents(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="er0r.me"))
        await self.bot.tree.sync()
        print(f"Logged in as {self.bot.user.name}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, I didn't recognize that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You're missing some required arguments.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the necessary permissions to use this command.")
        else:
            await ctx.send("An error occurred while processing the command.")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(f"{ctx.author} executed {ctx.command} in {ctx.guild} at {ctx.message.created_at}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return
        await self.handle_message_delete(message)

    async def handle_message_delete(self, message):
        embed = discord.Embed(
            title="Message Deleted",
            description=f"Nachricht von {message.author.name} wurde gelöscht.",
            color=discord.Color.red()
        )
        embed.add_field(name="Channel", value=message.channel.name, inline=True)
        embed.add_field(name="Message Content", value=message.content, inline=False)
        embed.add_field(name="Date", value=datetime.datetime.now().strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Time", value=datetime.datetime.now().strftime("%H:%M:%S"), inline=True)
        tracking_channel_id = self.tracking_channel_ids.get(message.guild.id)
        if tracking_channel_id:
            tracking_channel = self.bot.get_channel(tracking_channel_id)
            await tracking_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BotEvents(bot))
