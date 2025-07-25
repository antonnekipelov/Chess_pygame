from typing import List, Tuple, Optional
import pygame
from piece import Piece


class Bishop(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс слона (bishop)

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению слона
        """
        if texture_path is None:
            texture_path = f"assets/{color}_bishop.png"  # Путь по умолчанию
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для слона:
        - Движение только по диагоналям
        - Не может перепрыгивать через фигуры
        - Может брать фигуры противника
        """
        # Сначала базовая проверка (нельзя бить свои фигуры)
        if not super().is_valid_move(new_position, pieces):
            return False

        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]

        # Проверка на диагональное перемещение (|dx| == |dy|)
        if abs(dx) != abs(dy):
            return False

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        current_x, current_y = self.position[0] + \
            step_x, self.position[1] + step_y

        # Проверяем все клетки по пути
        while (current_x != new_position[0]) and (current_y != new_position[1]):
            for piece in pieces:
                if piece.position == (current_x, current_y):
                    return False  # Препятствие на пути
            current_x += step_x
            current_y += step_y

        # Проверка конечной клетки: либо пуста, либо с вражеской фигурой
        for piece in pieces:
            if piece.position == new_position:
                return piece.color != self.color  # Разрешено, если чужая фигура

        return True  # Клетка свободна

    def is_dark_square(self) -> bool:
        """
        Определяет, стоит ли слон на темной клетке
        (нужно для определения однопольных/разнопольных слонов)
        """
        return (self.position[0] + self.position[1]) % 2 != 0
