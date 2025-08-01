from typing import Optional, Tuple, List
from piece import Piece
from colors import Color
from constants import TILE_SIZE
import pygame

class Pawn(Piece):
    def __init__(self, parent_surface: pygame.Surface, pos: Tuple[int, int], 
                 color: Color, texture_path: Optional[str] = None):
        """
        Класс пешки (pawn)
        
        :param parent_surface: Поверхность для отрисовки
        :param pos: Начальная позиция (x, y)
        :param color: Цвет фигуры (Color.WHITE или Color.BLACK)
        :param texture_path: Опциональный путь к изображению пешки
        """
        if texture_path is None:
            texture_path = f"assets/bP.png" if color == Color.BLACK else f"assets/wP.png"
        super().__init__(parent_surface, pos, color, texture_path)
        self.en_passant_vulnerable = False  # Флаг "взятия на проходе"
        self.captured_piece = None
        self.prev_position = pos  # Добавляем запись предыдущей позиции

    def get_symbol(self) -> str:
        return "P"

    def is_valid_move(self, new_pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        old_x, old_y = self.position
        new_x, new_y = new_pos
        direction = -1 if self.color == Color.WHITE else 1  # Направление движения
        
        # Проверка базового движения вперед
        if new_x == old_x:
            # Движение на 1 клетку вперед
            if new_y == old_y + direction:
                return self._is_square_empty(new_pos, pieces)
            # Движение на 2 клетки из начальной позиции
            elif (new_y == old_y + 2*direction and 
                  not self.has_moved and 
                  self._is_square_empty((old_x, old_y + direction), pieces) and 
                  self._is_square_empty(new_pos, pieces)):
                self.en_passant_vulnerable = True
                return True
            return False
        
        # Проверка взятия (по диагонали)
        elif abs(new_x - old_x) == 1 and new_y == old_y + direction:
            # Обычное взятие
            for piece in pieces:
                if piece.position == new_pos and piece.color != self.color:
                    return True
            
            # Взятие на проходе
            if self.parent_board:
                last_pawn = self.parent_board.get_last_double_step_pawn()
                if (last_pawn and 
                    last_pawn.position == (new_x, old_y) and 
                    last_pawn.color != self.color):
                    return True
            return False
        
        return False

    def move_to(self, new_position: Tuple[int, int]):
        """Перемещает пешку на новую позицию с обработкой специальных правил"""
        old_x, old_y = self.position
        new_x, new_y = new_position
        
        # Обработка взятия на проходе
        if abs(new_x - old_x) == 1 and new_y == old_y + (-1 if self.color == Color.WHITE else 1):
            if self.parent_board:
                last_pawn = self.parent_board.get_last_double_step_pawn()
                if last_pawn and last_pawn.position == (new_x, old_y):
                    # Удаляем пешку, которая подверглась взятию на проходе
                    if last_pawn in self.parent_board.pieces:
                        self.parent_board.pieces.remove(last_pawn)
        self.prev_position = self.position
        super().move_to(new_position)
        self.en_passant_vulnerable = False  # Сбрасываем флаг после хода

    def resets_fifty_move_counter(self, new_pos: Tuple[int, int], pieces: list) -> bool:
        """Пешка всегда сбрасывает счетчик 50 ходов при ходе"""
        return True

    def _is_square_empty(self, pos: Tuple[int, int], pieces: List[Piece]) -> bool:
        """Проверяет, свободна ли клетка"""
        for piece in pieces:
            if piece.position == pos:
                return False
        return True

    def __str__(self):
        return f"{self.color.name} Pawn at {self.position}"