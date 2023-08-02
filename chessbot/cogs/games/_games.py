import discord
from discord.ext import commands

from constants import CHECK

from .chess.lobby import Chess_Lobby

class Games(commands.Cog, name="games"):
    """Games like Chess, Wordle or a flag guessing game."""
    COG_EMOJI = "🕹️"

    def __init__(self, bot:discord.Client):
        self.bot:discord.Client = bot

        self.chess_lobby = Chess_Lobby(max_matches=3)

    @commands.hybrid_command(description="Plays chess : @<challengee> | <move> | concede | help.")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    @discord.app_commands.describe(action='@<challengee>, <move>, concede, or help')
    async def chess(self, ctx: commands.Context, *, action):
        """
        Play a standard game of Chess with the bot or another user.
        Use `|h|chess info` for more information.
        """
        async with ctx.typing():
            ## Send help embed
            if action in ['info','help','?',None,'']:
                return await ctx.reply(embed=await self.chess_lobby.show_info_embed(ctx.clean_prefix),
                                    mention_author=False, ephemeral=False)
            ## List running chess matches
            if action in ['list matches','list']:
                return await ctx.reply(await self.chess_lobby.list_matches(),
                                    mention_author=False, ephemeral=False)            
            ## Concede
            elif action in ['concede','forfeit','quit','end']:
                myMatch, message = await self.chess_lobby.concede_match(ctx.message.author.id)
                if myMatch:
                    return await ctx.send(f"{CHECK} {message}")
                return await self.bot.send_warning(ctx, message)

            ## Challenge another user
            elif action.startswith('<@') and not ' ' in action and action.endswith('>'):
                challenger = ctx.message.author
                try:
                    challengee = await commands.MemberConverter().convert(ctx, action)
                except Exception as e:
                    return await self.bot.send_warning(ctx, f"{e}\nI could not challenge that user.")
                
                validate, black_robot, message = await self.chess_lobby.validate_new_match(
                    challenger, challengee, self.bot.user)
                if not validate:
                    return await self.bot.send_warning(ctx, message)
                if not black_robot:
                    reacted, rotate, message = await self.chess_lobby.get_reaction(
                        ctx, challenger, challengee)
                    if not reacted:
                        return await ctx.reply(message)
                else:
                    rotate = False

                board, message = await self.chess_lobby.create_match(
                    challenger_id=challenger.id, challenger_name=challenger.display_name,
                    challengee_id=challengee.id, challengee_name=challengee.display_name,
                    black_robot=black_robot, do_rotating=rotate)
                if not board:
                    return await self.bot.send_warning(ctx, message)
                return await ctx.send(message, file=board)

            ## Interpret action as a chess move
            else:
                board, message = await self.chess_lobby.make_move(
                    move=action, player_id=ctx.message.author.id)
                if not board:
                    return await self.bot.send_warning(ctx, message)
                return await ctx.send(message, file=board)

async def setup(bot: commands.bot):
    await bot.add_cog(Games(bot))