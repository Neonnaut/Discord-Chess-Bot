import cairosvg
import chess
import chess.engine
import chess.svg
from discord import File

chess_utils_folder = "cogs/games/chess"

class ChessPlayer:
    def __init__(self, id:int, name:str, colour:bool):
        self.id=id
        self.name=name.capitalize()
        self.colour:bool=colour
        self.colour_name:str = 'White' if colour else 'Black'
        self.moves = 0
        self.has_won = False

class ChessMatch:
    """One ChessGame for each match"""

    def __init__(self, white_player_id, white_player_name,
                 black_player_id, black_player_name, 
                 black_robot:bool, do_rotating = False):
        self.board = chess.Board()
        self.moves = 0

        self.white = ChessPlayer(white_player_id, white_player_name, chess.WHITE)
        self.black = ChessPlayer(black_player_id, black_player_name, chess.BLACK)

        self.black_robot = black_robot

        self.result = None # The results of the match when it ends (A string when ended)

        self.do_rotating = do_rotating # If to rotate board on turn
        self.black_robot = black_robot

        if not black_robot:
            self.engine = None
        else:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(f"{chess_utils_folder}/fairy-stockfish/fairy-stockfish-largeboard_x86-64")
            except:
                self.engine = chess.engine.SimpleEngine.popen_uci(f"{chess_utils_folder}/fairy-stockfish/fairy-stockfish-largeboard_x86-64.exe")
        
        self.player = self.white

    def get_white_player_id(self)-> int:
        return self.white.id
    def get_black_player_id(self)-> int:
        return self.black.id
    def get_player_id(self)-> int:
        return self.player.id
    def get_white_name(self)-> str:
        return self.white.name
    def get_black_name(self)-> str:
        return self.black.name
    def find_any_player_id(self, player_id:int)-> bool:
        if self.white.id == player_id:
            return True
        if self.black.id == player_id:
            return True
        return False
    def get_opponant_name(self, player_id:int)-> str:
        if self.white.id == player_id:
            return self.black.name
        return self.white.name
    def get_player_name(self, player_id:int)-> str:
        if self.white.id == player_id:
            return self.white.name
        return self.black.name
    
    def fetch_player_results(self):
        return self.white.id, self.white.has_won, self.black.id, self.black.has_won
        
    async def do_concede(self, player_id):
        if self.white.id == player_id:
            self.black.has_won = True
        else:
            self.white.has_won = True

    async def make_move(self, move:str):
        """Makes a chess move on the board and returns if it was valid, and the move object"""

        try:
            uci = chess.Move.from_uci(move)
        except ValueError as e:
            return (False, None)
        
        if uci in self.board.legal_moves:
            self.board.push(uci)
            self.player.moves += 1
            if self.board.is_game_over():
                await self.match_over()
                return True
            
            if self.black_robot:
                uci = self.engine.play(self.board, chess.engine.Limit(time=0.1)).move
                if uci in self.board.legal_moves:
                    # Make it the next player's turn
                    await self.change_player_turn()
                    self.board.push(uci)
                    self.player.moves += 1
                    if self.board.is_game_over():
                        await self.match_over()
                        return True

            # Make it the next player's turn
            await self.change_player_turn()
            return True
        return False

    async def change_player_turn(self):
        """Make it the next player's turn"""
        if self.player.colour == chess.WHITE:
            self.player = self.black
        elif self.player.colour == chess.BLACK:
            self.player = self.white

    async def match_over(self):
        """
        Formats the match over message.
        You can save results to a database here
        """
        win_method = self.board.outcome().termination.name.lower()
        if self.board.outcome().winner == chess.WHITE:
            self.white.has_won = True
            self.result = f"White, {self.white.name}, has won by {win_method} in {self.white.moves} moves."
        elif self.board.outcome().winner == chess.BLACK:
            self.black.has_won = True
            self.result = f"Black, {self.black.name}, has won by {win_method} in {self.black.moves} moves."
        else:
            self.result = f"The game has ended by {win_method}"

    async def print_chess_board(self):
        """Returns the board as an SVG and whos turn it is"""

        # Get if we rotate the board for the next player
        if self.do_rotating:
            if self.player.colour == chess.WHITE:
                orientation = True # White
            else:
                orientation = False # Black
        else:
            orientation = True # White

        check = None

        # Get the message to display with the embed
        if self.result == None:
            # If the game has not ended
            check_message = ''
            if self.board.is_check():
                check_message = '. You are in check.'
            happyMessage = f"{self.player.colour_name}'s turn now <@{self.player.id}>{check_message}"

            # Get the king index if the player is in check
            if self.board.is_check():
                if self.player.colour == chess.WHITE:
                    check = self.board.king(chess.WHITE)
                else:
                    check = self.board.king(chess.BLACK)
        else:
            # If the game has ended
            happyMessage = f"{self.result}"

            if self.board.is_checkmate():
                if self.player.colour == chess.WHITE:
                    check = self.board.king(chess.BLACK)
                else:
                    check = self.board.king(chess.WHITE)

        # Get the lastmove of the chess match
        try:
            lastmove = self.board.peek()
        except IndexError:
            lastmove = None

        # Create the board image
        svg = chess.svg.board(
            self.board,
            lastmove=lastmove,
            check=check,
            colors=
                dict.fromkeys("margin", "coord") | {"margin":"#202225", "coord":"#d6e8f5", "square light":"#dee3e6", "square dark":"#78bcde", "square light lastmove":"#cfe69e", "square dark lastmove":"#9dbf7c"},
            orientation=orientation
        )
        with open(f"{chess_utils_folder}/chessboard.svg", "w") as f:
            f.write(svg)
            cairosvg.svg2png(url=f"{chess_utils_folder}/chessboard.svg", write_to=f"{chess_utils_folder}/chessboard.png")
            board = File(f"{chess_utils_folder}/chessboard.png")

        return (board, happyMessage)