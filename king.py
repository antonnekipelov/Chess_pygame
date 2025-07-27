from typing import List, Tuple, Optional
import pygame
from colors import Color
from piece import Piece
from rook import Rook
from pawn import Pawn

class King(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        if texture_path is None:
            texture_path = f"assets/bK.png" if color == Color.BLACK else f"assets/wK.png"
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        if not super().can_move_to(new_position, pieces):
            return False

        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])

        # === РОКИРОВКА ===
        if dx == 2 and dy == 0 and not ignore_checks and self.move_count == 0:
            if self.is_under_attack(self.position, pieces):
                return False

            direction = 1 if new_position[0] > self.position[0] else -1
            rook_x = 7 if direction == 1 else 0
            rook_pos = (rook_x, self.position[1])

            # Ищем ладью для рокировки
            rook = None
            for piece in pieces:
                if (piece.position == rook_pos and isinstance(piece, Rook) 
                    and piece.color == self.color and piece.move_count == 0):
                    rook = piece
                    break

            if not rook:
                return False

            # Проверяем путь между королем и ладьей
            step_x = direction
            current_x = self.position[0] + step_x
            while current_x != rook_pos[0]:
                # Проверяем занятость клетки
                for piece in pieces:
                    if piece.position == (current_x, self.position[1]):
                        return False
                # Проверяем атаку на клетку
                if self.is_under_attack((current_x, self.position[1]), pieces):
                    return False
                current_x += step_x

            return True

        # === Обычный ход короля ===
        if dx > 1 or dy > 1:
            return False

        # Нельзя приближаться к вражескому королю
        for piece in pieces:
            if isinstance(piece, King) and piece.color != self.color:
                enemy_pos = piece.position
                if (abs(enemy_pos[0] - new_position[0]) <= 1 and 
                    abs(enemy_pos[1] - new_position[1]) <= 1):
                    return False

        if ignore_checks:
            return True

        # Проверка конечной позиции на шах
        temp_pieces = [p for p in pieces if p.position != new_position or p.color != self.color]
        for piece in temp_pieces:
            if piece.color != self.color and piece.is_valid_move(new_position, temp_pieces, True):
                return False

        return True

    def is_under_attack(self, pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        """Проверяет, находится ли позиция под атакой"""
        for piece in pieces:
            if piece.color != self.color:
                # Особый случай для пешек (атакуют по диагонали)
                if isinstance(piece, Pawn):
                    dir = -1 if piece.color == Color.WHITE else 1
                    if pos == (piece.position[0] + 1, piece.position[1] + dir) or\
                       pos == (piece.position[0] - 1, piece.position[1] + dir):
                        return True
                elif piece.is_valid_move(pos, pieces, True):
                    return True
        return False

    def do_castling_move(self, new_pos: Tuple[int, int], pieces: List[Piece]):
        """Выполняет рокировку, перемещая соответствующую ладью"""
        row = self.position[1]
        if new_pos[0] == 6:  # Короткая рокировка
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == (7, row):
                    piece.move_to((5, row))
                    break
        elif new_pos[0] == 2:  # Длинная рокировка
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == (0, row):
                    piece.move_to((3, row))
                    break