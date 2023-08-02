import datetime as dt
from discord import File, Embed
from ..chess.chess import (
    ChessMatch
)

class Chess_Lobby():
    def __init__(self, max_matches:int = 3):
        self.match_list = []
        self.max_matches = max_matches

    async def validate_new_match(self, challenger, challengee, bot
    )-> (tuple[None, None, str] | tuple[bool, bool, str]):
        """Tries to create a chess match. Returns board or None, and message"""
        if challengee.id == challenger.id:
            return None, None, 'You cannot challenge yourself'
        if await self.find_match(challenger.id):
            return None, None, f"You are already playing in a match"
        if len(self.match_list) >= self.max_matches:
            return None, None, f'Maximum amount of matches ({self.max_matches}) reached. '\
            + f'Please wait for the following matches to end:\n{await self.list_matches()}'
        if await self.find_match(challengee.id):        
            return None, None, "Your challengee is already playing a match"
    
        if challengee.bot and challengee.id != bot.id:
            return None, None, f"The only bot you can challenge is {bot.name}"
        
        black_robot = False
        if challengee.id == bot.id:
            black_robot = True

        return True, black_robot, "validated"
        
    async def create_match(self, challenger_id,challenger_name,challengee_id,challengee_name,
        black_robot:bool, do_rotating:bool=False
    )-> (tuple[None, str] | tuple[File, str]):
        """Tries to create a chess match. Returns board or None, and message"""            
        match = ChessMatch(
            white_player_id=challenger_id, white_player_name=challenger_name,
            black_player_id=challengee_id, black_player_name=challengee_name,
            black_robot=black_robot, do_rotating=do_rotating
        )
        self.match_list.append(match)

        board, happyMessage = await match.print_chess_board()
        return board, happyMessage
    
    async def make_move(self, move:str, player_id:int
        )->(tuple[None, str] | tuple[File, str]):
        """Tries to make a chess move. Returns board or None, and message"""
        move = str(move.replace(" ","")).casefold()
        if len(move) < 4 or len(move) > 5 or not move.isascii():
            return None, f"\"{move}\" is not a valid move. It should look like: 'a2b3'"
        match:ChessMatch = await self.find_match(player_id)
        if not match:
            return None, "You are not in a match"
        if not match.get_player_id() == player_id:
            return None, "It is not your turn"

        myMove = await match.make_move(move)
        if not myMove:
            return None, "That was not a valid move"
        board, happyMessage = await match.print_chess_board()

        if match.result:

            white_id, white_won, black_id, black_won = match.fetch_player_results()
            ## ASIGN ELO HERE
            await self.update_leaderboard(white_id, white_won, black_id, black_won)

        return board, happyMessage
    
    async def concede_match(self, player_id)->tuple[bool, str]:
        match:ChessMatch = await self.find_match(player_id)
        if not match:
            return False, "You are not in a match."
        await match.do_concede(player_id)
        conceder = match.get_player_name(player_id)
        concedee = match.get_opponant_name(player_id)

        white_id, white_won, black_id, black_won = match.fetch_player_results()
        ## ASIGN ELO HERE
        await self.update_leaderboard(white_id, white_won, black_id, black_won)

        self.match_list.remove(match)
        return True, f"{conceder} conceded to {concedee}."
        
    async def find_match(self, player_id: int)-> (None|ChessMatch):
        for match in self.match_list:
            if match.find_any_player_id(player_id):
                return match
        return None

    async def remove_match(self, player_id)-> bool:
        for match in self.match_list:
            if match.find_any_player_id(player_id):
                self.match_list.remove(match)
                return True
        return False
    
    async def update_leaderboard(self, white_id, white_won, black_id, black_won):
        # Get ELO

        # Recalculate ELO
        print(white_id, white_won, black_id, black_won)

        # Update ELO
        pass

    def recalculate_elo(self,
        player_1_elo, player_2_elo, 
        player_1_result, player_2_result
    ):
        """1 if player 1 wins / 0.5 if draw / 0 if player 2 wins"""
        KFACTOR = 24

        r1 = 10 ** (player_1_elo / 400)
        r2 = 10 ** (player_2_elo / 400)

        e1 = round(r1 / (r1 + r2),2)
        e2 = round(r2 / (r1 + r2),2)

        new_player_1_elo = int(player_1_elo + KFACTOR * (player_1_result - e1))
        if new_player_1_elo <= 100:
            new_player_1_elo = 100
        new_player_2_elo = int(player_2_elo + KFACTOR * (player_2_result - e2))
        if new_player_2_elo <= 100:
            new_player_2_elo = 100

        return new_player_1_elo, new_player_2_elo
    
    async def list_matches(self)-> str:
        return "=Running Chess Matches=\n"+'\n'.join([
            f'{match.get_white_name()} v {match.get_black_name()}'
            for match in self.match_list
        ]) or 'No matches are playing.'
    
    async def show_info_embed(self, prefix)-> Embed:
        """
        Generates an embed with information about chess
        """

        embed = Embed(
            title="Discord Chess",
            description="Play a standard game of Chess with the bot or another user.",
            colour=0x78bcde
        )
        embed.add_field(
            inline=False,
            name=f"**You can challenge a user, or this bot to a match with:**",
            value=
                f"`{prefix}chess @<user>`"
                " - The challengee then has six minutes to accept the challenge."
                "\nThis bot only runs three matches at the same time. "
                "You cannot challenge yourself. You cannot be in more than one match at one time"
        )
        embed.add_field(
            inline=False,
            name=f"**Concede defeat**",
            value=
                f"`{prefix}chess concede` - Ends the match prematurely.\nOther aliases are `end`, `forfeit` or `quit`"
        )
        embed.add_field(
            inline=False,
            name=f"**Chess move**",
            value=
                f"A move from a7 to a8 would be `{prefix}chess a7a8`\n"
                f"Or `{prefix}chess a7a8q` (if the latter is a promotion to a queen).\n"
                "Castling is done via the king moving into the castle's square."
        )
        return embed
    
    async def get_reaction(self, ctx, challenger, challengee)-> str:
        """Get confirmation from the user"""
        question = f"<@{challengee.id}> you have been challenged to a chess match by <@{challenger.id}>"+\
        "\nYou have 6 minutes to accept.\n\nChose the arrows emoji if you want the board to rotate for each turn."

        # Set to wait 6 minutes and set to return 'N' by default
        timeNow = dt.datetime.now()
        timeDelta = dt.timedelta(minutes=6)
        answered = False

        msg = await ctx.send(question)
        await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        await msg.add_reaction('\N{CROSS MARK}')
        await msg.add_reaction('\N{CLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}')

        while not answered and timeNow + timeDelta >= dt.datetime.now():
            msg = await msg.channel.fetch_message(msg.id)
            for reaction in msg.reactions:
                async for user in reaction.users():
                    # Make sure the reaction is not from a bot
                    if user.bot:
                        pass
                    elif user.id != challengee.id:
                        pass
                    elif reaction.emoji == '\N{WHITE HEAVY CHECK MARK}':
                        answered = True
                        return True, False, "The challenge was accepted"

                    elif reaction.emoji == '\N{CROSS MARK}':
                        answered = True
                        return False, False, "The challenge was not accepted"

                    elif reaction.emoji == '\N{CLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}':
                        answered = True
                        return True, True, "The challenge was accepted"

        return None, None, 'Time has ran out to react.'