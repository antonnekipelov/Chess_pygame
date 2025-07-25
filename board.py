import pygame
from typing import List, Optional
from colors import Color
from vector import Vector2i
from pawn import Pawn
from rook import Rook
from knight import Knight
from bishop import Bishop
from queen import Queen
from king import King

class Board:
    def __init__(self):
        self.TILE_SIZE = 64
        self.rows = 8
        self.cols = 8
        self.light_color = pygame.Color(240, 217, 181)  # Цвет светлых клеток
        self.dark_color = pygame.Color(181, 136, 99)    # Цвет темных клеток
        self.is_game_over = False
        self.tiles = []
        self.pieces = []
        self.current_turn = Color.WHITE
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.selected_piece = None
        self.move_list = []
        self.halfmove_clock = 0
        
        # Создаем поверхность для доски
        self.board_surface = pygame.Surface((self.cols * self.TILE_SIZE, self.rows * self.TILE_SIZE))
        self.create_board()
        self.add_pieces()
        
        # Инициализация выделения
        self.selection_rect = pygame.Rect(0, 0, self.TILE_SIZE, self.TILE_SIZE)
        self.selection_rect_color = pygame.Color(0, 128, 255, 76)
        self.selection_rect_visible = False

    def create_board(self):
        """Создает шахматную доску с клетками"""
        self.tiles = []
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                rect = pygame.Rect(col * self.TILE_SIZE, row * self.TILE_SIZE, 
                                 self.TILE_SIZE, self.TILE_SIZE)
                self.tiles.append((rect, color))

    def add_pieces(self):
        """Добавляет фигуры на доску в начальную позицию"""
        self.pieces = []
        
        # Черные фигуры
        for i in range(8):
            self.pieces.append(Pawn(self.board_surface, Vector2i(i, 1), "black"))
            
        self.pieces.append(Rook(self.board_surface, Vector2i(0, 0), "black"))
        self.pieces.append(Knight(self.board_surface, Vector2i(1, 0), "black"))
        self.pieces.append(Bishop(self.board_surface, Vector2i(2, 0), "black"))
        self.pieces.append(Queen(self.board_surface, Vector2i(3, 0), "black"))
        self.pieces.append(King(self.board_surface, Vector2i(4, 0), "black"))
        self.pieces.append(Bishop(self.board_surface, Vector2i(5, 0), "black"))
        self.pieces.append(Knight(self.board_surface, Vector2i(6, 0), "black"))
        self.pieces.append(Rook(self.board_surface, Vector2i(7, 0), "black"))
        
        # Белые фигуры
        for i in range(8):
            self.pieces.append(Pawn(self.board_surface, Vector2i(i, 6), "white"))
            
        self.pieces.append(Rook(self.board_surface, Vector2i(0, 7), "white"))
        self.pieces.append(Knight(self.board_surface, Vector2i(1, 7), "white"))
        self.pieces.append(Bishop(self.board_surface, Vector2i(2, 7), "white"))
        self.pieces.append(Queen(self.board_surface, Vector2i(3, 7), "white"))
        self.pieces.append(King(self.board_surface, Vector2i(4, 7), "white"))
        self.pieces.append(Bishop(self.board_surface, Vector2i(5, 7), "white"))
        self.pieces.append(Knight(self.board_surface, Vector2i(6, 7), "white"))
        self.pieces.append(Rook(self.board_surface, Vector2i(7, 7), "white"))

    def draw(self, surface):
        """Отрисовывает доску и фигуры на указанной поверхности"""
        # Рисуем клетки доски
        for rect, color in self.tiles:
            pygame.draw.rect(surface, color, rect)
        
        # Рисуем выделение
        if self.selection_rect_visible:
            s = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            s.fill(self.selection_rect_color)
            surface.blit(s, self.selection_rect)
        
        # Рисуем фигуры
        for piece in self.pieces:
            piece.draw(surface)
        
        # Рисуем подписи координат
        self.draw_coordinates(surface)

    def draw_coordinates(self, surface):
        """Рисует буквенно-цифровые координаты на доске"""
        font = pygame.font.SysFont("Arial", 16)
        letters = "ABCDEFGH"
        
        for i in range(8):
            # Буквы снизу и сверху
            text = font.render(letters[i], True, pygame.Color("white"))
            surface.blit(text, (i * self.TILE_SIZE + self.TILE_SIZE // 2 - text.get_width() // 2, 
                             self.rows * self.TILE_SIZE + 5))
            surface.blit(text, (i * self.TILE_SIZE + self.TILE_SIZE // 2 - text.get_width() // 2, -20))
            
            # Цифры слева и справа
            num = font.render(str(8 - i), True, pygame.Color("white"))
            surface.blit(num, (-20, i * self.TILE_SIZE + self.TILE_SIZE // 2 - num.get_height() // 2))
            surface.blit(num, (self.cols * self.TILE_SIZE + 5, 
                         i * self.TILE_SIZE + self.TILE_SIZE // 2 - num.get_height() // 2))

    def handle_click(self, pos):
        """Обрабатывает клик мыши на доске"""
        if self.is_game_over:
            return
            
        cell = Vector2i(pos[0] // self.TILE_SIZE, pos[1] // self.TILE_SIZE)
        
        if self.selected_piece:
            if self.selected_piece.is_valid_move(cell, self.pieces):
                self.process_move(cell)
            else:
                self.selected_piece = None
                self.selection_rect_visible = False
        else:
            self.select_piece(cell)

    def process_move(self, cell):
        """Обрабатывает перемещение фигуры"""
        prev_pos = self.selected_piece.position.copy()
        is_en_passant = False
        is_capture = False
        
        # Обработка взятия на проходе для пешки
        if isinstance(self.selected_piece, Pawn):
            direction = -1 if self.selected_piece.color == Color.WHITE else 1
            if abs(cell.x - prev_pos.x) == 1 and cell.y - prev_pos.y == direction:
                if (self.last_double_step_pawn and 
                    self.last_double_step_pawn.position == Vector2i(cell.x, prev_pos.y)):
                    self.pieces.remove(self.last_double_step_pawn)
                    is_en_passant = True
        
        # Проверка обычного взятия
        for p in self.pieces[:]:
            if p.position == cell and p.color != self.selected_piece.color:
                self.pieces.remove(p)
                is_capture = True
                break
        
        # Выполняем ход
        self.selected_piece.move_to(cell)
        
        # Обработка рокировки
        if isinstance(self.selected_piece, King) and abs(cell.x - prev_pos.x) == 2:
            self.selected_piece.do_castling_move(cell, self.pieces)
        
        # Обработка превращения пешки
        if isinstance(self.selected_piece, Pawn):
            y_end = 0 if self.selected_piece.color == Color.WHITE else 7
            if cell.y == y_end:
                self.promotion_pawn = self.selected_piece
                self.selected_piece = None
                self.show_promotion_popup()
                return
        
        # Обновление состояния игры
        self.update_game_state(prev_pos, cell, is_capture, is_en_passant)

    def update_game_state(self, prev_pos, cell, is_capture, is_en_passant):
        """Обновляет состояние игры после хода"""
        # Обновление счетчика 50 ходов
        if self.selected_piece.resets_fifty_move_counter(cell, self.pieces):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        if self.halfmove_clock >= 100:
            self.show_draw_popup("Draw by 50-move rule")
            self.is_game_over = True
        
        # Обновление флага двойного хода пешки
        self.last_double_step_pawn = None
        if isinstance(self.selected_piece, Pawn) and abs(cell.y - prev_pos.y) == 2:
            self.last_double_step_pawn = self.selected_piece
        
        # Смена хода, если не ожидается превращение
        if not self.promotion_pawn:
            self.switch_turn()
            if self.is_draw_by_material():
                self.is_game_over = True
        
        self.selected_piece = None
        self.selection_rect_visible = False

    def select_piece(self, cell):
        """Выбирает фигуру для хода"""
        for piece in self.pieces:
            if piece.position == cell and piece.color == self.current_turn:
                self.selected_piece = piece
                self.selection_rect_visible = True
                self.selection_rect.x = piece.position.x * self.TILE_SIZE
                self.selection_rect.y = piece.position.y * self.TILE_SIZE
                break

    def switch_turn(self):
        """Переключает текущего игрока"""
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def show_promotion_popup(self):
        """Показывает попап выбора фигуры для превращения пешки"""
        # Реализация попапа зависит от вашего UI
        pass

    def show_draw_popup(self, message):
        """Показывает попап с сообщением о ничьей"""
        # Реализация попапа зависит от вашего UI
        print(message)

    def is_draw_by_material(self):
        """Проверяет ничью по недостатку материала"""
        # Реализация проверки материала
        return False

    def new_game(self):
        """Начинает новую игру"""
        self.is_game_over = False
        self.pieces = []
        self.selected_piece = None
        self.selection_rect_visible = False
        self.current_turn = Color.WHITE
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.move_list = []
        self.halfmove_clock = 0
        self.add_pieces()