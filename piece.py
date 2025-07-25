import pygame
from typing import List
from constants import *
from vector import Vector2i
from colors import Color

class Piece:
    def __init__(self, parent_node, pos: Vector2i, clr: Color, texture_path: str):
        self.parent_ref = parent_node
        self.position = pos
        self.color = clr
        self.move_count = 0
        
        # Загрузка и масштабирование изображения
        try:
            self.image = pygame.image.load(texture_path)
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
            self.rect = self.image.get_rect()
            self._update_position()
        except FileNotFoundError:
            print(f"Ошибка загрузки изображения: {texture_path}")
            # Создаем временное изображение
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 255) if clr == Color.WHITE else (0, 0, 0))
            self.rect = self.image.get_rect()
            self._update_position()

    def _update_position(self):
        """Обновление позиции на экране"""
        self.rect.x = self.position.x * TILE_SIZE
        self.rect.y = self.position.y * TILE_SIZE

    def draw(self, screen):
        """Отрисовка фигуры на экране"""
        screen.blit(self.image, self.rect)

    def move_to(self, new_position: Vector2i):
        """Перемещение фигуры на новую позицию"""
        self.position = new_position
        self.move_count += 1
        self._update_position()

    def is_valid_move(self, new_position: Vector2i, pieces: List['Piece'], ignore_checks=False) -> bool:
        """Базовая проверка допустимости хода"""
        for piece in pieces:
            if piece.position == new_position and piece.color == self.color:
                return False
        return True
    def get_image(self):
        return self.image
    
    def is_capture_move(self, new_position:Vector2i,pices: List)->bool:
        for p in pices:
            if p.position == new_position and p.color !=self.color:
                return True
        return False
	
    def resets_fifty_move_counter(self, to_position: Vector2i, pices: List) -> bool:
        # По умолчанию — проверяем только на взятие
        for p in pices:
            if p.position == to_position and p.color != self.color:
                return True
        return False