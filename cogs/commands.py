import discord
from discord.ext import commands
from base_cog import BaseCog


class BotCommands(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.hybrid_command(name="whodis")
    async def help(self, ctx):
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

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong!")

async def setup(bot):
    await bot.add_cog(BotCommands(bot))
