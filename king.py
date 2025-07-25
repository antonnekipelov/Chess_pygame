from typing import List
from dataclasses import dataclass
from colors import Color
from pawn import Pawn
from piece import Piece
from rook import Rook
from vector import Vector2i


class King(Piece):
    def __init__(self, parent_node, pos: Vector2i, clr: str):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}K.png"
        super().__init__(parent_node, pos, clr, texture_path)
    
    def is_valid_move(self, new_position: Vector2i, pieces: List[Piece], ignore_checks=False) -> bool:
        if not super().is_valid_move(new_position, pieces, ignore_checks):  # ✅ фикс
            return False

        dx = abs(new_position.x - self.position.x)
        dy = abs(new_position.y - self.position.y)

        # === CASTLING ===
        if dx == 2 and dy == 0 and not ignore_checks and self.move_count == 0:
            if self._is_under_attack(self.position, pieces):
                return False

            direction = 1 if new_position.x > self.position.x else -1
            rook_x = 7 if direction == 1 else 0
            rook_pos = Vector2i(rook_x, self.position.y)

            for piece in pieces:
                if (piece.position == rook_pos and 
                    isinstance(piece, Rook) and 
                    piece.color == self.color and 
                    piece.move_count == 0):
                    
                    # Check if path is clear and not under attack
                    step = Vector2i(direction, 0)
                    current = self.position + step
                    while current != new_position + step:
                        for other in pieces:
                            if other.position == current:
                                return False
                        if self._is_under_attack(current, pieces):
                            return False
                        current += step
                    return True
            return False

        # === Normal king move (1 square) ===
        if dx > 1 or dy > 1:
            return False

        # Don't allow moving adjacent to enemy king
        for piece in pieces:
            if isinstance(piece, King) and piece.color != self.color:
                enemy_pos = piece.position
                if (abs(enemy_pos.x - new_position.x) <= 1 and 
                    abs(enemy_pos.y - new_position.y) <= 1):
                    return False

        if ignore_checks:
            return True

        # Check if move would put king in check
        adjusted_pieces = []
        for piece in pieces:
            if piece.position != new_position:
                adjusted_pieces.append(piece)
            elif piece.color == self.color:
                return False

        for piece in adjusted_pieces:
            if piece.color != self.color:
                if piece.is_valid_move(new_position, adjusted_pieces, True):
                    return False

        return True

    def _is_under_attack(self, pos: Vector2i, pieces: List[Piece]) -> bool:
        for piece in pieces:
            if piece.color != self.color:
                if isinstance(piece, Pawn):
                    if piece.attacks(pos, pieces):
                        return True
                else:
                    if piece.is_valid_move(pos, pieces, True):
                        return True
        return False


    def do_castling_move(self, new_pos: Vector2i, pieces: List[Piece]):
        row = self.position.y
        if new_pos.x == 6:  # Kingside castling
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == Vector2i(7, row):
                    piece.move_to(Vector2i(5, row))
                    break
        elif new_pos.x == 2:  # Queenside castling
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == Vector2i(0, row):
                    piece.move_to(Vector2i(3, row))
                    break
