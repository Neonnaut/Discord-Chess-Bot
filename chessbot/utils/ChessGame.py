import chess
import chess.svg

class ChessGame:
    """One ChessGame for each match"""

    def __init__(self, challenger, challengee):
        self.board = chess.Board()
        self.moves = 0
        self.player = challenger
        self.players = (challenger, challengee)

    def make_move(self, move):
        try:
            uci = chess.Move.from_uci(move)
        except ValueError as e:
            return False
        else:
            print("result"+self.board.result())
            if uci in self.board.legal_moves:
                
                self.board.push(uci)
                self.moves += 1
                
                if self.board.is_game_over():
                    return (True, self.board.result())
                else:
                    #self.board.apply_mirror()
                    #self.board.apply_transform(chess.flip_vertical)
                    self.player = self.players[self.moves % 2]
                    return (True, None)
            else:
                return (False, None)

    def board_to_svg(self):
        return chess.svg.board(self.board, size=350)
