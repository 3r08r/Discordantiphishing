import datetime
import discord
from discord.ext import commands
from .base_cog import BaseCog


class BotEvents(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

#command error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, I didn't recognize that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You're missing some required arguments.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the necessary permissions to use this command.")
        else:
            await ctx.send("An error occurred while processing the command.d")

# Command complete handler/ logger in console
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(f"{ctx.author} executed {ctx.command} in {ctx.guild} at {ctx.message.created_at}")

# nachrichten werden gelöscht handler
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_id = message.guild.id
        await self.handle_message_delete(message, guild_id)

# nachrichten gelöscht embed poster

    async def handle_message_delete(self, message, guild_id):
        try:    
            embed = discord.Embed(
                title="Nachricht wurde Gelöscht",
                description=f"Nachricht von {message.author.name} wurde gelöscht.",
                color=discord.Color.red()
            )
            embed.add_field(name="Channel", value=message.channel.name, inline=True)
            embed.add_field(name="Message Content", value=message.content, inline=False)
            embed.add_field(name="Date", value=datetime.datetime.now().strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Time", value=datetime.datetime.now().strftime("%H:%M:%S"), inline=True)
            embed.add_field(name="User", value=message.author.name, inline=True)
            tracking_channel_id = await self.get_tracking_channel_id(guild_id)
            if tracking_channel_id:
                tracking_channel = self.bot.get_channel(tracking_channel_id)
                if tracking_channel:
                    await tracking_channel.send(embed=embed)
                else:
                    print(f"Tracking channel not found for ID {tracking_channel_id}")
        except discord.DiscordException as e:
            print(f"Error handling phishing link: {e}")

    async def handle_phishing_link(self, message, url):
        try:
            guild_id = message.guild.id
            await message.delete()
            embed = self.create_embed(message, url)
            tracking_channel_id = await self.get_tracking_channel_id(guild_id)
            if tracking_channel_id:
                tracking_channel = self.bot.get_channel(tracking_channel_id)
                if tracking_channel:
                    await tracking_channel.send(embed=embed)
                else:
                    print(f"Tracking channel not found for ID {tracking_channel_id}")
        except discord.DiscordException as e:
            print(f"Error handling phishing link: {e}")

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
        try:
            guild_id = message.guild.id
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
            tracking_channel_id = await self.get_tracking_channel_id(guild_id)
            if tracking_channel_id:
                tracking_channel = self.bot.get_channel(tracking_channel_id)
                await tracking_channel.send(embed=embed)
        except discord.DiscordException as e:
            print(f"Error handling skibidi message: {e}")

async def setup(bot):
    await bot.add_cog(BotEvents(bot))
