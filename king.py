from typing import List, Tuple, Optional
import pygame
from colors import Color
from piece import Piece
from rook import Rook
from pawn import Pawn


class King(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: Color, texture_path: Optional[str] = None):
        if texture_path is None:
            texture_path = f"assets/bK.png" if color == Color.BLACK else f"assets/wK.png"
        super().__init__(parent_surface, pos, color, texture_path)
        self.has_moved = False

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece]) -> bool:
        if not super().is_valid_move(new_position, pieces):
            return False

        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])

        # === РОКИРОВКА ===
        if not self.has_moved and dx == 2 and dy == 0:
            if self.is_under_attack(self.position, pieces):
                return False

            direction = 1 if new_position[0] > self.position[0] else -1
            rook_x = 7 if direction == 1 else 0
            rook_pos = (rook_x, self.position[1])

            # Найти ладью
            rook = next((p for p in pieces if isinstance(p, Rook) and 
                    p.position == rook_pos and not p.has_moved and 
                    p.color == self.color), None)
            if not rook:
                return False

            # Определяем клетки, которые должен пройти король
            if direction == 1:  # Короткая рокировка
                king_path = [(self.position[0] + i, self.position[1]) for i in range(1, 3)]
            else:  # Длинная рокировка
                king_path = [(self.position[0] - i, self.position[1]) for i in range(1, 3)]

            # Проверяем свободны ли клетки и не находятся ли под атакой
            for pos in king_path:
                # Проверка на занятость клетки
                if any(p.position == pos for p in pieces):
                    return False
                # Проверка на атаку клетки
                if self.is_under_attack(pos, pieces):
                    return False

            return True

        # === Обычный ход короля ===
        if dx > 1 or dy > 1:
            return False

        # Проверяем, не будет ли король под шахом после хода
        if self.is_under_attack(new_position, pieces):
            return False

        # Нельзя приближаться к вражескому королю
        for piece in pieces:
            if isinstance(piece, King) and piece.color != self.color:
                enemy_pos = piece.position
                if abs(enemy_pos[0] - new_position[0]) <= 1 and abs(enemy_pos[1] - new_position[1]) <= 1:
                    return False

        return True

    def is_under_attack(self, pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        for piece in pieces:
            if piece.color != self.color:
                if isinstance(piece, Pawn):
                    dir = -1 if piece.color == Color.WHITE else 1
                    if pos == (piece.position[0] + 1, piece.position[1] + dir) or \
                    pos == (piece.position[0] - 1, piece.position[1] + dir):
                        return True
                elif isinstance(piece, King):
                    # Проверка соседних клеток вражеского короля
                    if abs(piece.position[0] - pos[0]) <= 1 and abs(piece.position[1] - pos[1]) <= 1:
                        return True
                else:
                    if piece.is_valid_move(pos, pieces):
                        return True
        return False


    def do_castling_move(self, new_pos: Tuple[int, int], pieces: List[Piece]):
        row = self.position[1]
        if new_pos[0] == 6:  # Короткая рокировка (0-0)
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == (7, row) and not piece.has_moved:
                    # Перемещаем ладью
                    piece.move_to((5, row))
                    break
        elif new_pos[0] == 2:  # Длинная рокировка (0-0-0)
            for piece in pieces:
                if isinstance(piece, Rook) and piece.position == (0, row) and not piece.has_moved:
                    # Перемещаем ладью
                    piece.move_to((3, row))
                    break