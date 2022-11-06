import cairosvg

import discord
from discord.ext import commands
from discord.utils import get

import utils.chessgame as chessgame # for the Discord-based Chess game

class Chess(commands.Cog, name="chess"):
    """Miscellaneous commands"""

    COG_EMOJI = "♟️"

    def __init__(self, bot):
        self.bot = bot
        #super().__init__()  # this is now required in this context.

        self.match_requests = []
        self.matches = []

    @commands.hybrid_command()
    async def challenge(self, ctx: commands.Context, chalengee: discord.User):
        """Challenges a user to a match"""

        challenger = ctx.message.author

        self.match_requests.append(chessgame.ChessGame(challenger, chalengee))
        await ctx.send(
            f"User <@{chalengee.id}> has been challenged!"
        )

    @commands.hybrid_command()
    async def accept(self, ctx: commands.Context):
        """Accepts a user's request"""

        message = ctx.message

        found = False
        for request in self.match_requests:
            # we have found the request
            if request.players[1].id == message.author.id:
                svg = request.board_to_svg()
                with open("utils/board.svg", "w") as f:
                    f.write(svg)
                    cairosvg.svg2png(url="utils/board.svg", write_to="utils/board.png")
                    fi = discord.File("utils/board.png")
                    await ctx.send(
                        f"Challenge from <@{request.players[0].id}> has been accepted!"
                    )
                    await ctx.send(
                        f"It is <@{request.player.id}>'s turn (White)", file=fi
                    )
                self.matches.append(request)
                self.match_requests.remove(request)
                found = True
        if not found:
            await ctx.send("No pending challenges!")

    @commands.hybrid_command()
    async def end(self, ctx: commands.Context):
        """Forfeits the match"""

        message = ctx.message

        found = False
        for match in self.matches:
            # we have found the match
            if match.player.id == message.author.id:
                found = True
                self.matches.remove(match)
                await ctx.send("Match forfeited.")
        if not found:
            await ctx.send("No match currently.")

    @commands.hybrid_command()
    async def move(self, ctx: commands.Context, *, move: str):
        """Makes move"""
        move = str(move.strip(" "))
        found = False
        for match in self.matches:
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
                    await ctx.send(f'Invalid move, "{move}".')
                else:
                    svg = match.board_to_svg()
                    with open("utils/board.svg", "w") as f:
                        f.write(svg)
                        cairosvg.svg2png(url="utils/board.svg", write_to="utils/board.png")
                        fi = discord.File("utils/board.png")
                        m = f"It is now <@{match.player.id}>'s turn"
                        if winner is not None:
                            m = f"{winner} wins!"
                        elif draw is True:
                            m = "The match was a draw!"
                        await ctx.send(m, file=fi)
                if result is not None:
                    self.matches.remove(match)
        if not found:
            await ctx.send("No match currently.")

async def setup(bot: commands.bot):
    await bot.add_cog(Chess(bot))
