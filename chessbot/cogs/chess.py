import cairosvg

import discord
from discord.ext import commands
from discord.utils import get

import utils.ChessGame as chessgame  # for the Discord-based Chess game

match_requests = []
matches = []

class Chess(commands.GroupCog, name="chess"):
    """Miscellaneous commands"""

    COG_EMOJI = "🏷️"

    def __init__(self, bot):
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @commands.hybrid_command()
    async def challenge(self, ctx: commands.Context, chalengee: discord.User):
        """Challenges user to a match"""
        challenger = ctx.message.author

        global match_requests

        match_requests.append(chessgame.ChessGame(challenger, chalengee))
        await ctx.send(
            f"User <@{chalengee.id}> has been challenged!"
        )

    @commands.hybrid_command()
    async def accept(self, ctx: commands.Context):
        """Accepts a user's request"""
        global match_requests
        global matches
        message = ctx.message

        found = False
        for request in match_requests:
            # we have found the request
            if request.players[1].id == message.author.id:
                svg = request.board_to_svg()
                with open("board.svg", "w") as f:
                    f.write(svg)
                    cairosvg.svg2png(url="board.svg", write_to="board.png")
                    fi = discord.File("board.png")
                    await ctx.send(
                        "Challenge from <@{0.id}> has been accepted!".format(
                            request.players[0]
                        )
                    )
                    await ctx.send(
                        "It is <@{0.id}>'s turn!".format(request.player), file=fi
                    )
                matches.append(request)
                match_requests.remove(request)
                found = True
        if not found:
            await ctx.send("No pending challenges!")

    @commands.hybrid_command()
    async def end(self, ctx: commands.Context):
        """Ends match, what a loser"""
        global matches

        message = ctx.message

        found = False
        for match in matches:
            # we have found the match
            if match.player.id == message.author.id:
                found = True
                matches.remove(match)
                await ctx.send("Match forfeited.")
        if not found:
            await ctx.send("No match currently.")

    @commands.hybrid_command()
    async def move(self, ctx: commands.Context, move: str):
        """Makes move"""
        move.strip(" ")
        global matches
        found = False
        for match in matches:
            # we have found the match
            if match.player.id == ctx.message.author.id:
                found = True
                valid, result = match.make_move(move)
                winner = None
                draw = False
                if result is not None:
                    if result == "1-0":
                        winner = match.player
                    elif result == "0-1":
                        winner = match.players[match.moves % 2]
                    elif result == "1/2-1/2":
                        draw = True
                if not valid:
                    await ctx.send("Invalid move, '{0}'".format(move))
                else:
                    svg = match.board_to_svg()
                    with open("board.svg", "w") as f:
                        f.write(svg)
                        cairosvg.svg2png(url="board.svg", write_to="board.png")
                        fi = discord.File("board.png")
                        m = "It is now <@{0.id}>'s turn!".format(match.player)
                        if winner is not None:
                            m = "<@{0.id}> wins!".format(winner)
                        elif draw is True:
                            m = "The match was a draw!"
                        await ctx.send(m, file=fi)
                if result is not None:
                    matches.remove(match)
        if not found:
            await ctx.send("No match currently.")

async def setup(bot: commands.bot):
    await bot.add_cog(Chess(bot))
