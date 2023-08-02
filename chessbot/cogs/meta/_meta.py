import discord
from discord.ext import commands

class Meta(commands.Cog, name="meta"):
    """Meta commands."""
    COG_EMOJI = "🔖"

    def __init__(self, bot: discord.Client):
        self.bot:discord.Client = bot

        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot: commands.bot):
    await bot.add_cog(Meta(bot))
