import chess
import chess.svg
from discord import Embed, File
import datetime as dt
import cairosvg

from __init__ import ERR

class ChessMatch:
    """One ChessGame for each match"""

    def __init__(self, challenger, challengee):
        self.board = chess.Board()
        self.moves = 0

        self.white = [challenger, "white"]
        self.black = [challengee, "black"]

        self.player = self.white

        self.result = None

    def make_move(self, move):
        try:
            uci = chess.Move.from_uci(move)
        except ValueError as e:
            return (False, None)
        else:
            if uci in self.board.legal_moves:
                
                self.board.push(uci)
                self.moves += 1
                
                if self.board.is_game_over():
                    
                    win_method = self.board.outcome().termination.name.lower()

                    if self.board.outcome().winner == chess.WHITE:
                        self.result = f"White, {self.white[0].display_name}, has won by {win_method}"
                    elif self.board.outcome().winner == chess.BLACK:
                        self.result = f"White, {self.black[0].display_name}, has won by {win_method}"
                    else:
                        self.result = f"{win_method}. The game is over"

                    return (True, self.board.result())
                    chess.Outcome.termination
                else:
                    #self.board.apply_mirror()
                    #self.board.apply_transform(chess.flip_vertical)
                    if self.player[1] == "white":
                        self.player = self.black
                    elif self.player[1] == "black":
                        self.player = self.white

                    return (True, None)
            else:
                return (False, None)

    def print_chess_board(self, move):
        svg = chess.svg.board(self.board, lastmove=move)

        with open("utils/board.svg", "w") as f:
            f.write(svg)
            cairosvg.svg2png(url="utils/board.svg", write_to="utils/board.png")
            board = File("utils/board.png")
        if self.result == None:
            # If the game has not ended
            check = ''
            if self.board.is_check():
                check = 'You are in check '
                print("check")
            return (f"{check}{self.player[1].capitalize()}'s turn now <@{self.player[0].id}>", board)
        else:
            # If the game has ended
            return (f"{self.result}", board)


def generate_info_embed() -> Embed:
    """
    Generates an embed with information about chess
    Returns:
        discord.Embed: The embed to be sent
    """

    embed = Embed(
        title="Discord Chess",
        description=
            "Play a standard game of Chess with another user."
    )
    embed.add_field(
        inline=False,
        name=f"**You can challenge a user to a match with:**",
        value=
            "`chess @user`"
            "\nThe challengee then has six minutes to accept the challenge."
            "\nThis bot only runs three matches at the same time. "
            "You cannot challenge yourself. You cannot be in more than one match at one time"
    )
    embed.add_field(
        inline=False,
        name=f"**Concede defeat**",
        value=
            "End the match prematurely with `chess concede`.\nOther aliases are `end`, `forfeit` and `quit`"
    )
    embed.add_field(
        inline=False,
        name=f"**Chess move**",
        value=
            "A move from a7 to a8 would be `chess a7a8`\nOr `chess a7a8q` (if the latter is a promotion to a queen)."
    )
    return embed

async def ynReaction(ctx, botID, challengeeID, question):
    """Get confirmation from the user"""

    timeNow = dt.datetime.now()
    timeDelta = dt.timedelta(minutes=6)
    answered = False
    output = 'N'

    msg = await ctx.send(question)
    await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    await msg.add_reaction('\N{CROSS MARK}')

    while not answered and timeNow + timeDelta >= dt.datetime.now():
        msg = await msg.channel.fetch_message(msg.id)
        for reaction in msg.reactions:
            async for user in reaction.users():
                # Make sure the reaction is not from the bot
                if user.id == botID:
                    pass
                elif user.id != challengeeID:
                    pass
                elif reaction.emoji == '\N{WHITE HEAVY CHECK MARK}':
                    answered = True
                    output = 'Y'

                elif reaction.emoji == '\N{CROSS MARK}':
                    answered = True
                    output = 'N'
    if not answered:
        output = 'N'
        await msg.channel.send(f'{ERR} You ran out of time.')

    return output