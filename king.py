from typing import List, Tuple, Optional
from colors import Color
from pawn import Pawn
from piece import Piece
from rook import Rook  # Для проверки рокировки
import pygame


class King(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс короля

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению короля
        """
        if texture_path is None:
            texture_path = f"assets/{color}_king.png"  # Путь по умолчанию
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для короля с учетом:
        - Обычного движения на 1 клетку
        - Рокировки
        - Не приближения к другому королю
        - Отсутствия шаха
        """
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

            # Поиск ладьи для рокировки
            rook = None
            for piece in pieces:
                if (isinstance(piece, Rook) and piece.position == rook_pos
                        and piece.color == self.color and piece.move_count == 0):
                    rook = piece
                    break

            if not rook:
                return False

            # Проверка пути на пустоту и отсутствие атаки
            step = (direction, 0)
            current = (self.position[0] + step[0], self.position[1] + step[1])
            while current != (new_position[0] + step[0], new_position[1] + step[1]):
                # Проверка на занятость клетки
                for piece in pieces:
                    if piece.position == current:
                        return False
                # Проверка на атаку клетки
                if self.is_under_attack(current, pieces):
                    return False
                current = (current[0] + step[0], current[1] + step[1])
            return True

        # === Обычный ход короля (1 клетка в любом направлении) ===
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

    def is_under_attack(self, pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        """Проверяет, находится ли позиция под атакой"""
        for piece in pieces:
            if piece.color != self.color:
                # Особый случай для пешек (атакуют по диагонали)
                if isinstance(piece, Pawn):
                    dir = -1 if piece.color == Color.WHITE else 1
                    if (pos == (piece.position[0] + 1, piece.position[1] + dir) or
                            pos == (piece.position[0] - 1, piece.position[1] + dir)):
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
