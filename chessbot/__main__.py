import aiohttp, logging, os
from difflib import SequenceMatcher

from discord import Activity, ActivityType, Intents
from discord.ext import commands

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from constants import DISCORD_CLIENT, PREFIX, TESTING, ERR, WARN


def main():
    bot = MyBot( # define an instance of the bot class to be run
        command_prefix=commands.when_mentioned_or(PREFIX),
        intents=Intents().all(), case_insensitive=True
    )
    bot.run(DISCORD_CLIENT, log_handler=None) # Run this bot instance

class MyBot(commands.Bot):
    async def setup_hook(self):
        # For HTTP requests
        self.session = aiohttp.ClientSession()
        # Create a custom logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(LoggerFormatter())
        self.logger.addHandler(ch)
        # Load cogs from the cogs folder
        for cog in sorted(os.listdir("./cogs")):
            if os.path.isdir(f"./cogs/{cog}") and not cog.startswith("__"):
                try:
                    await self.load_extension(f"cogs.{cog}._{cog}")
                except Exception as e:
                    self.logger.error(str(e))

    async def on_ready(self): # Prints that the bot is running
        await self.change_presence(activity=Activity(type=ActivityType.listening,
                                    name=f"{PREFIX}help"))
        self.logger.info(f'Logged in as '\
            f'{self.user.name} in {"testing" if TESTING else "working"} environment.')

    async def send_warning(self, ctx:commands.Context, myMessage:str):
        """Sends warning message and deletes both messages."""
        await ctx.reply(f"{WARN} {myMessage[:1].upper()}"\
            f"{myMessage[1:]}{''if str(myMessage)[-1]in['.','!','?']else'.'}",
            mention_author=False,delete_after=6)
        try:
            await ctx.message.delete(delay=6)
        except Exception:
            pass

    async def send_error(self, ctx:commands.Context, myMessage: str):
        """Sends error message and deletes both messages. Logs a warning."""
        await ctx.reply(f"{ERR} {myMessage[:1].upper()}"\
            f"{myMessage[1:]}{''if str(myMessage)[-1]in['.','!','?']else'.'}",
            mention_author=False,delete_after=8)
        try:
            await ctx.message.delete(delay=8)
        except Exception:
            pass
        self.logger.warning(myMessage)

    async def on_command_error(self, ctx: commands.Context, e): # Error messages
        try:
            if isinstance(e,(commands.CommandInvokeError, commands.HybridCommandError)):
                return await self.send_error(ctx, f"{e}")
            elif isinstance(e, commands.CommandNotFound):
                suggestion = ctx.message.content.replace(ctx.prefix, '').split(' ')
                available_commands = [cmd.name for cmd in self.commands]
                matches = {cmd: SequenceMatcher(None, cmd, suggestion[0]).ratio()
                    for cmd in available_commands}
                suggestion[0] = max(matches.items(), key=lambda item: item[1])[0]
                e=f"{e}. Did you mean `{ctx.prefix}{' '.join(suggestion)}`?"
            elif isinstance(e, commands.MissingRequiredArgument):
                e=f"{e} Run `{ctx.prefix}help {ctx.command}` for help on this command"
            return await self.send_warning(ctx, f"{e}")
        except:
            await ctx.author.send(f"{ERR} I did not have permission to respond to command "\
                +f"\"{ctx.message.content.replace(ctx.prefix, '').split(' ')[0][:20]}\""\
                +f" in \"{ctx.message.channel.name}\". "\
                +f"With error message: {e}{''if str(e)[-1]in['.','!','?']else'.'}")

class LoggerFormatter(logging.Formatter):
    """Logging Formatter to add colours and count warning / errors"""
    LEVEL_COLOURS = [(logging.DEBUG, '\x1b[36;1m'), (logging.NOTSET, '\x1b[37;1m'),
                    (logging.INFO, '\x1b[32;1m'), (logging.WARNING, '\x1b[33;1m'),
                    (logging.ERROR, '\x1b[31;1m'), (logging.CRITICAL, '\x1b[41;1m')]

    FORMATS={level:logging.Formatter(f'%(asctime)s.%(msecs)03d {colour}%(levelname)-8s'\
            f'\033[0m%(message)s \033[35m%(filename)s:%(funcName)s:%(lineno)d\033[0m',
            '%Y-%b-%d %H:%M:%S')
        for level, colour in LEVEL_COLOURS}

    def format(self,record):return self.FORMATS.get(record.levelno).format(record)

if __name__ == '__main__':
    main()