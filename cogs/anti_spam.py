import discord
from discord.ext import commands
from collections import defaultdict
import time
from datetime import datetime, timedelta
from typing import Dict, DefaultDict
from .base_cog import BaseCog

class AntiSpam(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        # Using defaultdict to avoid key errors
        self.message_count: DefaultDict[int, int] = defaultdict(int)
        self.last_message_time: Dict[int, float] = {}
        self.last_message_content: Dict[int, str] = {}
        
        # Spam configuration
        self.SPAM_THRESHOLD = 5  # Messages
        self.TIME_WINDOW = 5.0   # Seconds
        self.REPEAT_THRESHOLD = 2  # Repeated messages
        self.TIMEOUT_DURATION = 60  # Seconds

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not isinstance(message.author, discord.Member):
            return

        # Check immunity
        for role in message.author.roles:
            if await self.has_immunity_role(message.guild.id, role.id):
                return

        current_time = time.time()
        user_id = message.author.id

        try:
            
            if message.content:
                if user_id in self.last_message_content:
                    if message.content == self.last_message_content[user_id]:
                        await self.handle_spam(message, "message repetition")
                        return

            # Check message frequency
            if message.content:
                if user_id in self.last_message_time:
                    time_diff = current_time - self.last_message_time[user_id]
                    
                    if time_diff < self.TIME_WINDOW:
                        self.message_count[user_id] += 1
                        
                        if self.message_count[user_id] >= self.SPAM_THRESHOLD:
                            await self.handle_spam(message, "message frequency")
                            return
                    else:
                        # Reset counter if outside time window
                        self.message_count[user_id] = 1
    
            # Update tracking
            self.last_message_time[user_id] = current_time
            self.last_message_content[user_id] = message.content

        except Exception as e:
            print(f"Error in anti-spam: {str(e)}")

    async def handle_spam(self, message: discord.Message, reason: str):
        try:
            await message.delete()
            timeout_until = discord.utils.utcnow() + timedelta(seconds=self.TIMEOUT_DURATION)
            await message.author.timeout(timeout_until, reason=f"Spam detection: {reason}")
            
            # Trigger mod log
            self.bot.dispatch("mod_action", 
                action_type="Message Deleted (Spam)",
                user=message.author,
                reason=reason,
                message=message
            )

            # Notify the user
            try:
                await message.author.send(
                    f"You have been timed out for {self.TIMEOUT_DURATION} seconds due to {reason}. "
                    "Please avoid spamming in the server."
                )
            except discord.Forbidden:
                pass  # Can't DM the user
            
            # Reset their spam counter
            user_id = message.author.id
            self.message_count[user_id] = 0
            
        except discord.Forbidden:
            print(f"Missing permissions to timeout {message.author}")
        except Exception as e:
            print(f"Error handling spam: {str(e)}")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))