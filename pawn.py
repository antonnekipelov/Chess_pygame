from typing import List
from piece import Piece
from vector import Vector2i
from colors import Color
from constants import TILE_SIZE

class Pawn(Piece):
    def __init__(self, parent_node, pos: Vector2i, clr: Color):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}p.png"
        super().__init__(parent_node, pos, clr, texture_path)
        self.en_passant_vulnerable = False

    def is_valid_move(self, new_position: Vector2i, pieces: List[Piece], ignore_checks=False) -> bool:
        if not super().is_valid_move(new_position, pieces, ignore_checks):
            return False
            
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1

        # Обычный ход вперед
        if new_position.x == self.position.x:
            for p in pieces:
                if p.position == new_position:
                    return False
            
            if new_position.y == self.position.y + direction:
                return True
            
            if (self.position.y == start_row and 
                new_position.y == self.position.y + 2 * direction):
                between = Vector2i(self.position.x, self.position.y + direction)
                for p in pieces:
                    if p.position == between or p.position == new_position:
                        return False
                return True

        # Взятие по диагонали (включая на проходе)
        elif abs(new_position.x - self.position.x) == 1:
            if new_position.y == self.position.y + direction:
                for p in pieces:
                    if p.position == new_position and p.color != self.color:
                        return True
                
                if self._can_en_passant(new_position, pieces):
                    return True

        return False

    def _can_en_passant(self, target_pos: Vector2i, pieces: List[Piece]) -> bool:
        if not hasattr(self.parent_ref, 'get_last_double_step_pawn'):
            return False
            
        last_pawn = self.parent_ref.get_last_double_step_pawn()
        if not last_pawn or not isinstance(last_pawn, Pawn):
            return False
            
        return (last_pawn.color != self.color and
                last_pawn.position == Vector2i(target_pos.x, self.position.y) and
                last_pawn.en_passant_vulnerable)

    def attacks(self, target_pos: Vector2i, pieces: List[Piece]) -> bool:
        direction = -1 if self.color == Color.WHITE else 1
        dx = target_pos.x - self.position.x
        dy = target_pos.y - self.position.y
        return abs(dx) == 1 and dy == direction

    def move_to(self, new_position: Vector2i):
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1
        
        if (self.position.y == start_row and 
            abs(new_position.y - self.position.y) == 2):
            self.en_passant_vulnerable = True
        else:
            self.en_passant_vulnerable = False
            
        super().move_to(new_position)

    def resets_fifty_move_counter(self, to_position: Vector2i, pices: list) -> bool:
	    # Пешка всегда сбрасывает счётчик, даже если не взяла
	    return True
