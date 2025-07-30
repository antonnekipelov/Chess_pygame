import pygame
from typing import Tuple, Optional
from colors import Color
from constants import TILE_SIZE

class Piece:
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], 
                 color: Color, texture_path: Optional[str] = None):
        """
        Базовый класс для шахматных фигур

        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y) на доске
        :param color: Цвет фигуры (Color.WHITE или Color.BLACK)
        :param texture_path: Путь к изображению фигуры
        """
        self.screen = parent_surface
        self.position = pos  # (x, y) координаты на доске
        self.color = color
        self.parent_board = None  # Ссылка на родительскую доску
        self.sprite = None
        self.has_moved = False  # Для отслеживания первого хода
        
        if texture_path:
            try:
                self.sprite = pygame.image.load(texture_path)
                self.sprite = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE))
            except Exception as e:
                print(f"Error loading sprite: {e}")
                self.sprite = None

    def move_to(self, new_position: Tuple[int, int]):
        """Перемещает фигуру на новую позицию"""
        self.position = new_position
        self.has_moved = True

    def draw(self):
        """Отрисовывает фигуру на доске"""
        x = self.position[0] * TILE_SIZE
        y = self.position[1] * TILE_SIZE
        
        if self.sprite:
            self.screen.blit(self.sprite, (x, y))
        else:
            # Резервный вариант отрисовки, если нет спрайта
            color = (255, 255, 255) if self.color == Color.WHITE else (0, 0, 0)
            pygame.draw.circle(self.screen, color, 
                             (x + TILE_SIZE//2, y + TILE_SIZE//2), 
                             TILE_SIZE//3)
            
            # Добавляем буквенное обозначение фигуры
            font = pygame.font.SysFont('Arial', 24)
            symbol = self.get_symbol()
            text_color = (0, 0, 0) if self.color == Color.WHITE else (255, 255, 255)
            text = font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(x + TILE_SIZE//2, y + TILE_SIZE//2))
            self.screen.blit(text, text_rect)

    def draw_on_surface(self, surface, pos):
        """Отрисовывает фигуру на указанной поверхности (для меню превращения)"""
        if self.sprite:
            surface.blit(self.sprite, pos)
        else:
            # Резервный вариант отрисовки
            color = (255, 255, 255) if self.color == Color.WHITE else (0, 0, 0)
            pygame.draw.circle(surface, color, 
                             (pos[0] + TILE_SIZE//2, pos[1] + TILE_SIZE//2), 
                             TILE_SIZE//3)
            
            font = pygame.font.SysFont('Arial', 24)
            symbol = self.get_symbol()
            text_color = (0, 0, 0) if self.color == Color.WHITE else (255, 255, 255)
            text = font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(pos[0] + TILE_SIZE//2, pos[1] + TILE_SIZE//2))
            surface.blit(text, text_rect)

    def get_symbol(self) -> str:
        """Возвращает символьное обозначение фигуры (для текстовой отрисовки)"""
        return "?"

    def is_valid_move(self, new_pos: Tuple[int, int], pieces: list) -> bool:
        """Базовая проверка, общая для всех фигур"""
        # Нельзя оставаться на месте
        if new_pos == self.position:
            return False
            
        # Нельзя бить свои фигуры
        for piece in pieces:
            if piece.position == new_pos and piece.color == self.color:
                return False
                
        return True  # Базовые проверки пройдены

    def resets_fifty_move_counter(self, new_pos: Tuple[int, int], pieces: list) -> bool:
        """
        Определяет, сбрасывает ли этот ход счетчик 50 ходов
        (по умолчанию - взятие или ход пешкой сбрасывает счетчик)
        """
        # Проверка на взятие
        for piece in pieces:
            if piece.position == new_pos and piece.color != self.color:
                return True
                
        return False

    def __str__(self):
        return f"{self.color.name} {self.__class__.__name__} at {self.position}"