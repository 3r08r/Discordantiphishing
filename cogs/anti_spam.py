import time
import discord
import json
from discord.ext import commands
from .base_cog import BaseCog


class AntiSpam(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.message_count = {}
        self.last_message_time = {}
        self.last_message_content = {}
        self.timeout_end = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        current_time = time.time()


        if message.author.id in self.timeout_end and current_time < self.timeout_end[message.author.id]:
            await message.delete()
            return


        if message.author.id in self.last_message_content and message.content == self.last_message_content[
            message.author.id]:
            await message.delete()
            try:
                await message.author.send("Please do not repeat the same message.")
            except discord.errors.Forbidden:
                print(f"Unable to send DM to {message.author}")


        if message.author.id in self.last_message_time and current_time - self.last_message_time[message.author.id] < 2:
            self.message_count[message.author.id] = self.message_count.get(message.author.id, 0) + 1
            if self.message_count[message.author.id] > 4:
                self.timeout_end[message.author.id] = current_time + 20
            else:
                self.last_message_time[message.author.id] = current_time
        else:
            self.message_count[message.author.id] = 1
            self.last_message_time[message.author.id] = current_time

        self.last_message_content[message.author.id] = message.content


async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
