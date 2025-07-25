from typing import List, Optional, Tuple
from colors import Color
from piece import Piece  # Импортируем базовый класс фигуры
import pygame


class Pawn(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс пешки

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению пешки
        """
        if texture_path is None:
            texture_path = f"assets/{color}_pawn.png"  # Путь по умолчанию
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для пешки с учетом особых правил:
        - Обычное движение вперед
        - Двойной ход с начальной позиции
        - Взятие по диагонали
        - Взятие на проходе
        """
        if not super().can_move_to(new_position, pieces):
            return False

        if ignore_checks:
            return False

        direction = -1 if self.color == Color.WHITE else 1  # Направление движения
        start_row = 6 if self.color == Color.WHITE else 1   # Стартовая линия

        # Обычное движение вперед на 1 клетку
        if new_position[0] == self.position[0] and new_position[1] == self.position[1] + direction:
            for p in pieces:
                if p.position == new_position:
                    return False  # Клетка занята
            return True

        # Двойной ход с начальной позиции
        if (self.position[1] == start_row and
            new_position[0] == self.position[0] and
                new_position[1] == self.position[1] + 2 * direction):

            # Проверяем промежуточную клетку
            between_pos = (self.position[0], self.position[1] + direction)
            for p in pieces:
                if p.position == new_position or p.position == between_pos:
                    return False  # Путь заблокирован
            return True

        # Взятие по диагонали
        if (abs(new_position[0] - self.position[0]) == 1 and
                new_position[1] == self.position[1] + direction):

            # Обычное взятие
            for p in pieces:
                if p.position == new_position and p.color != self.color:
                    return True

            # Взятие на проходе (требует доступа к родительской доске)
            if hasattr(self, 'parent_board') and hasattr(self.parent_board, 'get_last_double_step_pawn'):
                last_pawn = self.parent_board.get_last_double_step_pawn()
                if (last_pawn and isinstance(last_pawn, Pawn) and last_pawn.color != self.color):
                    if last_pawn.position == (new_position[0], self.position[1]):
                        return True

        return False

    def attacks(self, target_pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        """Пешка атакует по диагонали вперед"""
        direction = -1 if self.color == Color.WHITE else 1
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        return abs(dx) == 1 and dy == direction

    def resets_fifty_move_counter(self, to_position: Tuple[int, int], pieces: List[Piece]) -> bool:
        """Пешка всегда сбрасывает счетчик 50 ходов (даже без взятия)"""
        return True
