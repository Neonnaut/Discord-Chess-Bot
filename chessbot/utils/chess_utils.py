import cairosvg
import chess
import chessdotcom
import chess.svg
import datetime as dt
import json
import requests
import time
from discord import Embed, File

class ChessMatch:
    """One ChessGame for each match"""

    def __init__(self, challenger, challengee):
        self.board = chess.Board()
        self.moves = 0

        self.white = [challenger, "white"]
        self.black = [challengee, "black"]

        self.player = self.white

        self.winner = None

        self.result = None # The results of the match when it ends (A string when ended)

    def get_white_player_id(self):
        return self.white[0].id
    def get_black_player_id(self):
        return self.black[0].id
    def get_player_id(self):
        return self.player[0].id
    def get_white_player_name(self):
        return self.white[0].name
    def get_black_player_name(self):
        return self.black[0].name

    def make_move(self, move):
        """Makes a chess move on the board and returns if it was valid, and the move object"""

        try:
            uci = chess.Move.from_uci(move)
        except ValueError as e:
            return (False, None)
        else:
            if uci in self.board.legal_moves:
                
                self.board.push(uci)
                self.moves += 1
                
                if self.board.is_game_over():
                    
                    self.match_over()

                    return (True, uci)
                else:
                    #self.board.apply_mirror()
                    #self.board.apply_transform(chess.flip_vertical)

                    # Make it the next player's turn
                    if self.player[1] == "white":
                        self.player = self.black
                    elif self.player[1] == "black":
                        self.player = self.white

                    return (True, uci)
            else:
                return (False, None)

    def match_over(self):
        """
        Formats the match over message.
        You can save results to a database here
        """

        win_method = self.board.outcome().termination.name.lower()
        if self.board.outcome().winner == chess.WHITE:
            self.winner = self.white
            self.result = f"White, {self.get_white_player_name()}, has won by {win_method} in {self.moves} moves"
        elif self.board.outcome().winner == chess.BLACK:
            self.winner = self.black
            self.result = f"Black, {self.get_black_player_name()}, has won by {win_method} in {self.moves} moves"
        else:
            self.result = f"The game has ended by {win_method}"

    def print_chess_board(self, move):
        """Returns the board as an SVG and the player whos turn it is"""

        svg = chess.svg.board(self.board, lastmove=move)

        with open("utils/board.svg", "w") as f:
            f.write(svg)
            cairosvg.svg2png(url="utils/board.svg", write_to="utils/board.png")
            board = File("utils/board.png")
        if self.result == None:
            # If the game has not ended
            check = ''
            if self.board.is_check():
                check = '. You are in check'
                print("check")
            return (f"{self.player[1].capitalize()}'s turn now <@{self.player[0].id}>{check}", board)
        else:
            # If the game has ended
            return (f"{self.result}", board)


def generate_chess_info_embed() -> Embed:
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
            "A move from a7 to a8 would be `chess a7a8`\n"
            "Or `chess a7a8q` (if the latter is a promotion to a queen).\n"
            "Castling is done via the king moving into the castle's square."
    )
    return embed

async def get_reaction(ctx, botID, challengeeID, question):
    """Get confirmation from the user"""

    # Set to wait 6 minutes and set to return 'N' by default
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
        await msg.channel.send('Time has ran out to react.')

    return output

def generate_chessdotcom_embed(player) -> Embed:
    try:
        pp = chessdotcom.get_player_profile(player).json["player"]
        ps = chessdotcom.get_player_stats(player).json["stats"]
    except:
        return False

    embed = Embed(
        title = pp["username"].capitalize(),
        url = pp["url"],
        description = 'Player info and stats'
    )

    try:
        embed.set_thumbnail(url=pp["avatar"])
    except:
        pass

    embed.add_field(
        name = "Country",
        value = getCountry(pp["country"]),
        inline = True
    )
    embed.add_field(
        name = "Date Joined:",
        value = time.strftime("%a %x", time.gmtime(pp["joined"])),
        inline = True
    )
    embed.add_field(
        name = "Last Online:",
        value = time.strftime("%a %x", time.gmtime(pp["last_online"])),
        inline = True
    )

    try:
        embed.add_field(
            name = "FIDE",
            value = ps["fide"],
            inline = False
        )
    except:
        pass

    try:
        embed.add_field(
            name = "Rapid",
            value =
            f'Win: **{ps["chess_rapid"]["record"]["win"]}**, '
            f'Loss: **{ps["chess_rapid"]["record"]["win"]}**, '
            f'Draw: **{ps["chess_rapid"]["record"]["win"]}**\n'
            f'Highest Rating: **{ps["chess_rapid"]["best"]["rating"]}**',
            inline = False)
    except:
        pass

    try:
        embed.add_field(
            name = "Bullet",
            value =
            f'Win: **{ps["chess_bullet"]["record"]["win"]}**, '
            f'Loss: **{ps["chess_bullet"]["record"]["win"]}**, '
            f'Draw: **{ps["chess_bullet"]["record"]["win"]}**\n'
            f'Highest Rating: **{ps["chess_bullet"]["best"]["rating"]}**',
            inline = False)
    except:
        pass

    try:
        embed.add_field(
            name = "Blitz",
            value =
            f'Win: **{ps["chess_blitz"]["record"]["win"]}**, '
            f'Loss: **{ps["chess_blitz"]["record"]["win"]}**, '
            f'Draw: **{ps["chess_blitz"]["record"]["win"]}**\n'
            f'Highest Rating: **{ps["chess_blitz"]["best"]["rating"]}**',
            inline = False)
    except:
        pass

    return embed

def getCountry(site):
    r = requests.get(site)
    text = r.text
    countryISOData = json.loads(text)
    name = countryISOData['name']
    emoji  = f""":flag_{site.replace("https://api.chess.com/pub/country/", '').lower()}:"""
    specialString = f"{emoji} {name}"
    return specialString