# __init__.py
from .anti_phishing import AntiPhishing
from .backup import BackupCog
from .base_cog import BaseCog
from .commands import BotCommands
from .events import BotEvents
from .utilities import utilities
from .anti_spam import AntiSpam


async def setup(bot):
    await bot.add_cog(AntiPhishing(bot))
    await bot.add_cog(AntiSpam(bot))
    await bot.add_cog(BackupCog(bot))
    await bot.add_cog(BaseCog(bot))
    await bot.add_cog(BotCommands(bot))
    await bot.add_cog(BotEvents(bot))
    await bot.add_cog(utilities(bot))
