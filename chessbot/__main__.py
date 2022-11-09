import logging
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher
from discord import Intents

from discord.ext import commands
from discord.utils import _ColourFormatter

from __init__ import ERR, TOKEN

os.chdir(os.path.dirname(os.path.realpath(__file__))) # Directoy that __main__.py is in is now root directory if it wasn't

logger = logging.getLogger() # Create logger (allows discord.py and our logs to be shown on the terminal)
logger.setLevel(logging.INFO) # Set level to info (ignores debug logs)
ch = logging.StreamHandler() # Create console handler
ch.setFormatter(_ColourFormatter()) # Add discord.py's custom formatter to ch
logger.addHandler(ch) # Add ch to logger

def main():
    bot = MyBot( # Define an instance of this bot
        command_prefix=commands.when_mentioned_or(*["!!", "++"]),
        intents=Intents().all(),
        case_insensitive=True
    )
    load_dotenv()
    bot.run(TOKEN, log_handler=None) # Run this bot instance


class MyBot(commands.Bot):
    async def setup_hook(self):
        for cog in sorted(os.listdir("./cogs")): # Load all the cogs / extensions in the cogs folder
            if cog.endswith(".py") and not cog.startswith("_"):
                try:
                    await self.load_extension("cogs." + cog[:-3])
                except Exception as e:
                    logger.error(str(e))

    async def on_ready(self): # Prints that the bot is running
        logger.info(f'Logged in as {self.user.name}')

        await self.tree.sync()  # Sync any slash commands the bot has set up

    async def on_command_error(self, ctx: commands.Context, e): # Error messages
        if isinstance(e, commands.CommandNotFound):
            message = ctx.message  # Later overwrite the attributes
            used_prefix = ctx.prefix  # The prefix used
            used_command = message.content.split()[0][len(used_prefix):]  # Getting the command, `!foo a b c` -> `foo`

            available_commands = [cmd.name for cmd in self.commands]
            matches = {  # command name: ratio
                cmd: SequenceMatcher(None, cmd, used_command).ratio()
                for cmd in available_commands
            }

            command = max(matches.items(), key=lambda item: item[1])[0]  # The most similar command

            try:
                arguments = message.content.split(" ", 1)[1]
            except IndexError:
                arguments = ""  # Command didn't take any arguments

            new_content = f"{used_prefix}{command} {arguments}".strip()

            await ctx.channel.send(f"{ERR} Command \"{used_command}\" was not found.\n"+\
                f"Did you mean: `{new_content}`?")
        if isinstance(e, commands.MissingRequiredArgument):
            await ctx.send(f"{ERR} Missing required arguments."
                        + f"Run `{ctx.clean_prefix}help {ctx.command}` for help on this command.")
            # "Missing required arguments. Run !!help _ for help on this command."
        if isinstance(e, commands.NotOwner):
            await ctx.send(f"{ERR} {e}")
            # You do not own this bot.
        if isinstance(e, commands.MissingPermissions):
            await ctx.send(f"{ERR} {e}")
            # "You are missing Administrator permission(s) to run this command."
        if isinstance(e, commands.CommandOnCooldown):
            await ctx.send(f"{ERR} {e}.")
            # "You are on cooldown. Try again in _."
        if isinstance(e, commands.BadArgument):
            await ctx.send(f"{ERR} {e}.")
            # "bad argument _."
        elif isinstance(e, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f"{ERR} {e}")
                # "This command cannot be used in private messages."
            except:
                pass

if __name__ == '__main__':
    main()
