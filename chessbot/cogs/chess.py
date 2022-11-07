import cairosvg
import datetime as dt

import discord
from discord.ext import commands
from discord.utils import get
from discord import app_commands

import chess

import utils.chessgame as chessgame # for the Discord-based Chess game

from utils.chessgame import (
    ChessMatch,
    generate_info_embed,
    ynReaction
)

from __init__ import ERR, CHECK, WARN, INFO

class ChessCog(commands.Cog, name="Chess"):
    """Miscellaneous commands"""

    COG_EMOJI = "♟️"

    def __init__(self, bot):
        self.bot = bot

        self.matches = []

    @commands.hybrid_command()
    async def challenge(self, ctx: commands.Context, challengee: discord.User):
        """Challenges a user to a match"""

        challenger = ctx.message.author

        if challenger == challengee:
            followMessage = await ctx.send(f"{ERR} You cannot challenge yourself")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass
        elif challengee.bot:
            followMessage = await ctx.send(f"{ERR} You cannot challenge any bots")
            try:
                await followMessage.delete(delay=5)
            except Exception:
                pass
        else:
            found = False
            # Go through all the matches
            for match in self.matches:
                # if the current turn's chess player's id is the command user id
                if match.white[0].id == challenger.id or match.black[0].id == challenger.id:
                    found = True
                    followMessage = await ctx.send(f"{ERR} You are already playing a match.")
                    try:
                        await followMessage.delete(delay=5)
                    except Exception:
                        pass
                elif match.white[0].id == challengee.id or match.black[0].id == challengee.id:
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
                if await ynReaction(ctx, self.bot.user.id, challengee.id, confMessage) == 'Y':
                    # Got response from user
                    if len(self.matches) >= 3:
                        await ctx.send(f"{ERR} There are already three chess matches playing at the same time!\n"
                        f"{self.matches[0].white[0].name} v {self.matches[0].black[0].name}\n"
                        f"{self.matches[1].white[0].name} v {self.matches[1].black[0].name}\n"
                        f"{self.matches[2].white[0].name} v {self.matches[2].black[0].name}\n\n"
                        "Please wait for these matches to finish and try challenging again.")
                    else:
                        # create match
                        match = chessgame.ChessMatch(challenger, challengee)
                        self.matches.append(match)
                        
                        board = match.print_chess_board(None)
                        await ctx.send(f"{CHECK}The challenge has been accepted.\n" + board[0], file=board[1]
                        )
                else:
                    # Ran out of time or was deleted
                    await ctx.send(f"{INFO} The challenge was not accepted")

    @commands.hybrid_command()
    async def move(self, ctx: commands.Context, move: str):
        """Makes move"""

        move = str(move.replace(" ",""))
        if len(move) < 4 or len(move) > 5:
            # "a1b" move was too few characters
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
                if match.player[0].id == ctx.message.author.id:
                    found = True
                    valid, result = match.make_move(move)
                    winner = None
                    draw = False
                    if result is not None:
                        if result == "1-0":
                            winner = match.player[0]
                        elif result == "0-1":
                            if match.player[1] == "black":
                                winner = match.white[0].display_name
                            else:
                                winner = match.black[0].display_name
                        elif result == "1/2-1/2":
                            draw = True
                    if not valid:
                        followMessage = await ctx.send(f'{WARN} Invalid move, "{move}".')
                        try:
                            await followMessage.delete(delay=5)
                        except Exception:
                            pass
                    else:

                        svg = chess.svg.board(match.board, lastmove=chess.Move.from_uci(move))
                        with open("utils/board.svg", "w") as f:
                            f.write(svg)
                            cairosvg.svg2png(url="utils/board.svg", write_to="utils/board.png")
                            fi = discord.File("utils/board.png")
                            m = f"{match.player[1].capitalize()}'s turn now <@{match.player[0].id}>"
                            if winner is not None:
                                m = f"{winner} wins!"
                            elif draw is True:
                                m = "The match was a draw!"
                            await ctx.send(m, file=fi)
                    if result is not None:
                        self.matches.remove(match)
            if not found:
                followMessage = await ctx.send(f"{INFO} You are not playing, or it is not your turn.")
                try:
                    await followMessage.delete(delay=5)
                except Exception:
                    pass

    @commands.hybrid_command()
    async def concede(self, ctx: commands.Context):
        """Concedes the match"""
        found = False
        for match in self.matches:
            # we have found the match
            if match.player[0].id == ctx.message.author.id:
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

    @commands.hybrid_command()
    async def info(self, ctx: commands.Context):
        """Shows info about Discor Chess"""
        await ctx.reply(embed=generate_info_embed(), mention_author=False, ephemeral=False)


    """
    @commands.hybrid_command()
    async def chess(self, ctx, action):
        ""Plays chess | challenge:\"@user\"; move:\"a1a2\"; concede:\"concede\"; Info:\"info\"""

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

async def setup(bot: commands.bot):
    await bot.add_cog(ChessCog(bot))