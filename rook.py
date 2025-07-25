from typing import List, Tuple, Optional
import pygame
from piece import Piece


class Rook(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс ладьи (rook)

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению ладьи
        """
        if texture_path is None:
            texture_path = f"assets/{color}_rook.png"  # Путь по умолчанию
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для ладьи:
        - Движение только по горизонтали или вертикали
        - Не может перепрыгивать через фигуры
        - Может брать фигуры противника
        """
        # Проверка что не пытаемся пойти в ту же клетку
        if new_position == self.position:
            return False

        # Проверка движения строго по горизонтали или вертикали
        if new_position[0] != self.position[0] and new_position[1] != self.position[1]:
            return False

        # Определяем направление движения
        step_x = 0
        step_y = 0

        if new_position[0] != self.position[0]:  # Горизонтальное движение
            step_x = 1 if new_position[0] > self.position[0] else -1
        else:  # Вертикальное движение
            step_y = 1 if new_position[1] > self.position[1] else -1

        # Проверяем все клетки по пути
        current_x = self.position[0] + step_x
        current_y = self.position[1] + step_y

        while current_x != new_position[0] or current_y != new_position[1]:
            # Проверяем каждую клетку на пути
            for piece in pieces:
                if piece.position == (current_x, current_y):
                    return False  # Путь заблокирован

            current_x += step_x
            current_y += step_y

        # Проверка конечной клетки
        for piece in pieces:
            if piece.position == new_position:
                return piece.color != self.color  # Можно брать вражеские фигуры

        return True  # Ход допустим
