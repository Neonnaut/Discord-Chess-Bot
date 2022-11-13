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
    async def chess(self, ctx: commands.Context, action):
        ""Plays chess | challenge:\"@user\" | move:\"a1a2\" | \"concede\" | \"help\".""

        match action:
            case "concede" | "forfeit" | "quit":
                # Then concede
                await self.concede(ctx)
            case None | "info" | "help":
                # Send help embed
                await ctx.reply(embed=generate_chess_info_embed(ctx.clean_prefix), mention_author=False, ephemeral=False)
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
    async def challenge(
        self,
        ctx: commands.Context,
        challengee: discord.User,
    ):
        """Challenges a user to a chess match"""

        challenger = ctx.message.author

        if challenger == challengee:
            await ctx.send(f"{ERR} You cannot challenge yourself.", delete_after=5)
        elif challengee.bot:
            await ctx.send(f"{ERR} You cannot challenge bots.", delete_after=5)
        else:
            found = False
            # Go through all the matches
            for match in self.matches:
                # if the current turn's chess player's id is the command user id
                if match.get_white_id() == challenger.id or match.get_black_id() == challenger.id:
                    found = True
                    await ctx.send(f"{ERR} You are already playing a match.", delete_after=5)
                elif match.get_white_id() == challengee.id or match.get_black_id() == challengee.id:
                    found = True
                    await ctx.send(f"{ERR} Your challengee is already playing a match.", delete_after=5)
            if not found:
                # Ask the challengee to accept the challenge through reactions within 6 minutes
                confMessage = f"<@{challengee.id}> you have been challenged to a chess match by <@{challenger.id}>"+\
                "\nYou have 6 minutes to accept.\n\nChose the arrows emoji if you want the board to rotate for each turn."
                reaction =  await get_reaction(ctx, self.bot.user.id, challengee.id, confMessage)
                rotate = False
                if reaction == 'X':
                    rotate = True
                if reaction == 'Y' or rotate:
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
                        match = ChessMatch(challenger, challengee, rotate)
                        self.matches.append(match)
                        # Print the board
                        happyMessage, board = match.print_chess_board()
                        await ctx.send(f"{CHECK} The challenge has been accepted.\n" + happyMessage, file=board)
                else:
                    # Ran out of time or was deleted
                    await ctx.send(f"{INFO} The challenge did not accept.")

    @commands.hybrid_command()
    @commands.guild_only()
    async def move(self, ctx: commands.Context, move: str):
        """Makes chess move"""
        move = str(move.replace(" ",""))
        if len(move) < 4 or len(move) > 5:
            # "a1b" move was too few characters or too much
            await ctx.send(f"{INFO} \"{move}\" is not a valid move. It should look like: `chess a2b3`", delete_after=5)
        else:
            # a7a8q move was the right amount of characters
            found = False
            # Go through all the matches
            for match in self.matches:
                # if the current turn's chess player's id is the command user id
                if match.get_player_id() == ctx.message.author.id:
                    found = True
                    # Make the chess move
                    valid = match.make_move(move)
                    if valid:
                        # Print the board
                        happyMessage, board = match.print_chess_board()
                        await ctx.send(happyMessage, file=board)
                        # Delete match if game won
                        if match.result is not None:
                            self.matches.remove(match)
                    else:
                        await ctx.send(f'{WARN} Invalid move, "{move}".', delete_after=5)
            if not found:
                await ctx.send(f"{INFO} You are not playing, or it is not your turn.", delete_after=5)

    @commands.hybrid_command()
    @commands.guild_only()
    async def concede(self, ctx: commands.Context):
        """Concedes the chess match"""
        found = False
        for match in self.matches:
            # we have found the match
            if match.get_black_player_id() == ctx.message.author.id or match.get_white_player_id() == ctx.message.author.id:
                found = True
                # Remove the match
                self.matches.remove(match)
                await ctx.send(f"{CHECK} Match forfeited.")
        if not found:
            await ctx.send(f"{INFO} You are not in a match.", delete_after=5)

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
            await ctx.reply(f"{ERR} Could not find the username \"{username}\"", delete_after=5)

async def setup(bot: commands.bot):
    await bot.add_cog(Chess(bot))