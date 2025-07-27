from typing import List, Tuple, Optional
import pygame
from colors import Color
from piece import Piece


class Knight(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Класс коня (knight)

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению коня
        """
        if texture_path is None:
            texture_path = f"assets/bN.png" if color == Color.BLACK else f"assets/wN.png"
        super().__init__(parent_surface, pos, color, texture_path)

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List[Piece], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода для коня (буквой "Г")

        :param new_position: Новая позиция (x, y)
        :param pieces: Список всех фигур на доске
        :param ignore_checks: Игнорировать проверку шаха (не используется для коня)
        :return: True если ход допустим
        """
        # Сначала проверяем базовые условия (нельзя бить свои фигуры)
        if not super().is_valid_move(new_position, pieces):
            return False

        dx = abs(new_position[0] - self.position[0])
        dy = abs(new_position[1] - self.position[1])

        # Конь ходит буквой "Г" - 2 клетки в одном направлении и 1 в перпендикулярном
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
