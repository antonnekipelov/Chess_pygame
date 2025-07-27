import pygame
from typing import List, Tuple, Optional

from colors import Color


class Piece:
    TILE_SIZE = 64

    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], color: str, texture_path: Optional[str] = None):
        """
        Базовый класс для шахматной фигуры

        :param parent_surface: Поверхность для отрисовки (экран или доска)
        :param pos: Позиция на доске в клетках (x, y)
        :param color: Цвет фигуры ('white' или 'black')
        :param texture_path: Путь к изображению фигуры
        """
        self.parent_surface = parent_surface
        self.position = pos
        self.color = color
        self.move_count = 0

        # Загрузка текстуры или создание заглушки
        if texture_path:
            try:
                self.texture = pygame.image.load(texture_path)
                self.texture = pygame.transform.scale(
                    self.texture, (self.TILE_SIZE, self.TILE_SIZE))
            except:
                self.texture = self._create_dummy_texture()
        else:
            self.texture = self._create_dummy_texture()

    def _create_dummy_texture(self) -> pygame.Surface:
        """Создает временную текстуру для фигуры"""
        surface = pygame.Surface(
            (self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        color = (255, 255, 255) if self.color == Color.WHITE else (50, 50, 50)
        pygame.draw.circle(surface, color, (self.TILE_SIZE //
                           2, self.TILE_SIZE//2), self.TILE_SIZE//3)
        return surface

    def move_to(self, new_position: Tuple[int, int]):
        """Перемещает фигуру на новую позицию"""
        self.position = new_position
        self.move_count += 1

    def draw(self):
        """Отрисовывает фигуру на доске"""
        if hasattr(self, 'texture'):
            x = self.position[0] * self.TILE_SIZE
            y = self.position[1] * self.TILE_SIZE
            self.parent_surface.blit(self.texture, (x, y))

    def is_valid_move(self, new_position: Tuple[int, int], pieces: List['Piece'], ignore_checks: bool = False) -> bool:
        """
        Проверяет допустимость хода

        :param new_position: Новая позиция (x, y)
        :param pieces: Список всех фигур на доске
        :param ignore_checks: Игнорировать проверку шаха
        :return: True если ход допустим
        """
        for piece in pieces:
            if piece.position == new_position and piece.color == self.color:
                return False
        return True

    def can_move_to(self, new_position: Tuple[int, int], pieces: List['Piece']) -> bool:
        """Проверяет, может ли фигура переместиться на клетку"""
        for piece in pieces:
            if piece.position == new_position and piece.color == self.color:
                return False
        return True

    def attacks(self, target_pos: Tuple[int, int], pieces: List['Piece']) -> bool:
        """Проверяет, атакует ли фигура указанную позицию"""
        return self.is_valid_move(target_pos, pieces, True)

    def is_capture_move(self, new_position: Tuple[int, int], pieces: List['Piece']) -> bool:
        """Проверяет, является ли ход взятием"""
        for p in pieces:
            if p.position == new_position and p.color != self.color:
                return True
        return False

    def resets_fifty_move_counter(self, to_position: Tuple[int, int], pieces: List['Piece']) -> bool:
        """
        Определяет, сбрасывает ли ход счетчик 50 ходов
        (по умолчанию - только при взятии)
        """
        for p in pieces:
            if p.position == to_position and p.color != self.color:
                return True
        return False

    def copy(self) -> 'Piece':
        """Создает копию фигуры"""
        return type(self)(self.parent_surface, self.position, self.color, getattr(self, 'texture_path', None))