from typing import List, Tuple, Optional
import pygame
from piece import Piece
from rook import Rook
from bishop import Bishop


class Queen(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс ферзя (queen)

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению ферзя
        """
        if texture_path is None:
            texture_path = f"assets/{color}_queen.png"  # Путь по умолчанию
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для ферзя:
        - Комбинирует движения ладьи и слона
        - Движение по горизонтали, вертикали или диагонали
        - Не может перепрыгивать через фигуры
        - Может брать фигуры противника
        """
        # Сначала проверяем базовые условия
        if not super().is_valid_move(new_position, pieces):
            return False

        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]

        # Ферзь ходит как ладья или слон
        # Проверяем движение по прямой (как ладья)
        if dx == 0 or dy == 0:
            # Используем логику ладьи
            step_x = 0
            step_y = 0

            if dx != 0:  # Горизонтальное движение
                step_x = 1 if dx > 0 else -1
            else:  # Вертикальное движение
                step_y = 1 if dy > 0 else -1

            current_x = self.position[0] + step_x
            current_y = self.position[1] + step_y

            while current_x != new_position[0] or current_y != new_position[1]:
                for piece in pieces:
                    if piece.position == (current_x, current_y):
                        return False
                current_x += step_x
                current_y += step_y

        # Проверяем движение по диагонали (как слон)
        elif abs(dx) == abs(dy):
            step_x = 1 if dx > 0 else -1
            step_y = 1 if dy > 0 else -1

            current_x = self.position[0] + step_x
            current_y = self.position[1] + step_y

            while current_x != new_position[0] and current_y != new_position[1]:
                for piece in pieces:
                    if piece.position == (current_x, current_y):
                        return False
                current_x += step_x
                current_y += step_y
        else:
            return False  # Не диагональ и не прямая

        # Проверка конечной клетки
        for piece in pieces:
            if piece.position == new_position:
                return piece.color != self.color

        return True
