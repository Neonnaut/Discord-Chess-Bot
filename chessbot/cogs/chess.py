import discord
from discord.ext import commands

from utils.chess_utils import (
    ChessMatch,
    generate_chess_info_embed,
    generate_chessdotcom_embed,
    get_reaction
)

from __init__ import ERR, CHECK, WARN, INFO

class Chess(commands.Cog, name="Chess"):
    """Commands for playing chess"""

    COG_EMOJI = "♟️"

    def __init__(self, bot):
        self.bot = bot

        self.matches = []

    """
    @commands.hybrid_command()
    async def chess(self, ctx, action):
        ""Plays chess | challenge:\"@user\", move:\"a1a2\", \"concede\", \"help\".""

        match action:
            case "concede" | "forfeit" | "quit":
                # Then concede
                await self.concede(ctx)
            case None | "info" | "help":
                # Send help embed
                await ctx.reply(embed=generate_info_embed(), mention_author=False, ephemeral=False)
            case _:
                try:
                    # Challenge another user
                    challengee = await commands.MemberConverter().convert(ctx, action)
                    await self.challenge(ctx, challengee)
                except:
                    # Interpret action as a chess move
                    await self.move(ctx, action)
    """

    @commands.hybrid_command()
    @commands.guild_only()
    async def challenge(self, ctx: commands.Context, challengee: discord.User):
        """Challenges a user to a chess match"""

        challenger = ctx.message.author

        if challenger == challengee:
            followMessage = await ctx.send(f"{ERR} You cannot challenge yourself")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass
        elif challengee.bot:
            followMessage = await ctx.send(f"{ERR} You cannot challenge bots")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass
        else:
            found = False
            # Go through all the matches
            for match in self.matches:
                # if the current turn's chess player's id is the command user id
                if match.get_white_id() == challenger.id or match.get_black_id() == challenger.id:
                    found = True
                    followMessage = await ctx.send(f"{ERR} You are already playing a match.")
                    try:
                        await followMessage.delete(delay=5)
                    except Exception:
                        pass
                elif match.get_white_id() == challengee.id or match.get_black_id() == challengee.id:
                    found = True
                    followMessage = await ctx.send(f"{ERR} Your challengee is already playing a match.")
                    try:
                        await followMessage.delete(delay=5)
                    except Exception:
                        pass
            if not found:
                # Ask the challengee to accept the challenge through reactions within 6 minutes
                confMessage = f"<@{challengee.id}> you have been challenged to a chess match by <@{challenger.id}>"+\
                "\nYou have 6 minutes to accept."
                if await get_reaction(ctx, self.bot.user.id, challengee.id, confMessage) == 'Y':
                    # Got response from user
                    if len(self.matches) >= 3:
                        match_list = ""
                        for match in self.matches:
                            match_list += f"{match.get_white_name()} v {match.get_black_name()}\n"
                        await ctx.send(f"{ERR} There are already three chess matches playing at the same time!\n"
                        f"{match_list}"
                        "Please wait for these matches to finish and try challenging again.")
                    else:
                        # MAGIC STARTS HERE
                        # Create a match and append to current matches
                        match = ChessMatch(challenger, challengee)
                        self.matches.append(match)
                        # Print the board
                        happyMessage, board = match.print_chess_board(None)
                        await ctx.send(f"{CHECK} The challenge has been accepted.\n" + happyMessage, file=board)
                else:
                    # Ran out of time or was deleted
                    await ctx.send(f"{INFO} The challenge was not accepted")

    @commands.hybrid_command()
    @commands.guild_only()
    async def move(self, ctx: commands.Context, move: str):
        """Makes a chess move"""

        move = str(move.replace(" ",""))
        if len(move) < 4 or len(move) > 5:
            # "a1b" move was too few characters or too much
            followMessage = await ctx.send(f"{INFO} \"{move}\" is not a valid move. It should look like: `chess a2b3`")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass
        else:
            # a7a8q move was the right amount of characters
            found = False
            # Go through all the matches
            for match in self.matches:
                # if the current turn's chess player's id is the command user id
                if match.get_player_id() == ctx.message.author.id:
                    found = True
                    # Make the chess move
                    valid, done_move = match.make_move(move)
                    if valid:
                        # Print the board
                        happyMessage, board = match.print_chess_board(done_move)
                        await ctx.send(happyMessage, file=board)
                        # Delete match if game won
                        if match.result is not None:
                            self.matches.remove(match)
                    else:
                        followMessage = await ctx.send(f'{WARN} Invalid move, "{move}".')
                        try:
                            await followMessage.delete(delay=5)
                        except Exception:
                            pass
            if not found:
                followMessage = await ctx.send(f"{INFO} You are not playing, or it is not your turn.")
                try:
                    await followMessage.delete(delay=5)
                except Exception:
                    pass

    @commands.hybrid_command(aliases=["quit","forfeit","end"])
    @commands.guild_only()
    async def concede(self, ctx: commands.Context):
        """Concedes the chess match"""
        found = False
        for match in self.matches:
            # we have found the match
            if match.get_player_id() == ctx.message.author.id:
                found = True
                # Remove the match
                self.matches.remove(match)
                await ctx.send(f"{CHECK} Match forfeited.")
        if not found:
            followMessage = await ctx.send(f"{INFO} You are not in a match.")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass

    @commands.hybrid_command(aliases=["rules"])
    @commands.guild_only()
    async def info(self, ctx: commands.Context):
        """Shows info about Discord Chess"""
        await ctx.reply(embed=generate_chess_info_embed(), mention_author=False, ephemeral=False)

    @commands.hybrid_command(aliases=["profile","chessdotcom"])
    @commands.guild_only()
    async def chessdotcom_profile(self, ctx, username):
        """Displays a profile found on Chess.com"""
        embed=generate_chessdotcom_embed(username)
        if embed:
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"{ERR} Could not find the username \"{username}\"")

async def setup(bot: commands.bot):
    await bot.add_cog(Chess(bot))