import pygame
from typing import List, Tuple, Optional
from colors import Color
from constants import *
from pawn import Pawn
from piece import Piece
from rook import Rook
from knight import Knight
from bishop import Bishop
from queen import Queen
from king import King

class Board:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((COLS * TILE_SIZE + 300, ROWS * TILE_SIZE))
        pygame.display.set_caption("Chess")

        self.pieces = []
        self.current_turn = Color.WHITE
        self.selected_piece = None
        self.show_selection = False
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.halfmove_clock = 0
        self.is_game_over = False
        self.move_list = []
        
        # Для меню превращения
        self.show_promotion_menu = False
        self.promotion_options = []
        self.promotion_rects = []

        self.selection_rect = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.selection_rect.fill((0, 128, 255, 80))

        self.font = pygame.font.SysFont('Arial', 16)
        self.turn_label = self.create_label("Ход: белые", (COLS * TILE_SIZE + 20, 20))

        self.create_board()
        self.add_pieces()

    def create_board(self):
        self.tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                self.tiles.append((row, col, color))

    def add_pieces(self):
        self.pieces.clear()

        # Черные пешки
        for i in range(8):
            p1 = Pawn(self.screen, (i, 1), Color.BLACK)
            p1.parent_board = self
            self.pieces.append(p1)

        # Черные фигуры
        back_row_black = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(back_row_black):
            piece = cls(self.screen, (i, 0), Color.BLACK)
            piece.parent_board = self
            self.pieces.append(piece)

        # Белые пешки
        for i in range(8):
            p2 = Pawn(self.screen, (i, 6), Color.WHITE)
            p2.parent_board = self
            self.pieces.append(p2)

        # Белые фигуры
        back_row_white = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(back_row_white):
            piece = cls(self.screen, (i, 7), Color.WHITE)
            piece.parent_board = self
            self.pieces.append(piece)

    def get_last_double_step_pawn(self):
        return self.last_double_step_pawn

    def create_label(self, text, pos):
        label = self.font.render(text, True, (0, 0, 0))
        return (label, pos)

    def draw(self):
        self.screen.fill((255, 255, 255))
        
        # Рисуем клетки доски
        for row, col, color in self.tiles:
            pygame.draw.rect(self.screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Рисуем фигуры
        for piece in self.pieces:
            piece.draw()

        # Рисуем выделение выбранной фигуры
        if self.show_selection and self.selected_piece:
            x = self.selected_piece.position[0] * TILE_SIZE
            y = self.selected_piece.position[1] * TILE_SIZE
            self.screen.blit(self.selection_rect, (x, y))

        # Рисуем меню превращения
        if self.show_promotion_menu and self.promotion_pawn:
            self.draw_promotion_menu()

        # Рисуем метку текущего хода
        self.screen.blit(self.turn_label[0], self.turn_label[1])
        
        pygame.display.flip()

    def draw_promotion_menu(self):
        if not self.promotion_pawn:
            return
            
        x = self.promotion_pawn.position[0] * TILE_SIZE
        y = self.promotion_pawn.position[1] * TILE_SIZE
        color = self.promotion_pawn.color
        
        # Корректируем позицию меню, чтобы оно не выходило за границы доски
        if y < 2 * TILE_SIZE:
            menu_y = 0
        else:
            menu_y = y - 4 * TILE_SIZE  # Меню из 4 вариантов
            
        # Создаем поверхность для меню
        menu_surface = pygame.Surface((TILE_SIZE, 4 * TILE_SIZE), pygame.SRCALPHA)
        menu_surface.fill((200, 200, 200, 200))
        
        # Варианты превращения
        options = [Queen, Rook, Bishop, Knight]
        self.promotion_options = []
        self.promotion_rects = []
        
        for i, piece_class in enumerate(options):
            # Создаем временную фигуру для отображения
            piece = piece_class(self.screen, (0, 0), color)
            piece.parent_board = self
            self.promotion_options.append(piece)
            
            # Запоминаем прямоугольники для обработки кликов
            rect = pygame.Rect(x, menu_y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            self.promotion_rects.append(rect)
            
            # Рисуем фон для варианта превращения
            option_rect = pygame.Rect(0, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(menu_surface, (220, 220, 220) if i % 2 == 0 else (180, 180, 180), option_rect)
            
            # Рисуем фигуру
            piece.draw_on_surface(menu_surface, (0, i * TILE_SIZE))
        
        # Рисуем меню на экране
        self.screen.blit(menu_surface, (x, menu_y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Обработка клика в меню превращения
                if self.show_promotion_menu and self.promotion_pawn:
                    for i, rect in enumerate(self.promotion_rects):
                        if rect.collidepoint(mouse_pos):
                            self.promote_pawn(self.promotion_options[i])
                            return True
                    
                    # Клик вне меню - отменяем превращение
                    self.show_promotion_menu = False
                    self.promotion_pawn = None
                    return True
                
                # Обычная обработка клика по доске
                cell = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

                if self.is_game_over:
                    return True

                if self.selected_piece:
                    if self.selected_piece.is_valid_move(cell, self.pieces):
                        prev_pos = self.selected_piece.position
                        is_capture = False
                        is_castling = False
                        is_en_passant = False

                        # Взятие на проходе
                        if isinstance(self.selected_piece, Pawn):
                            direction = -1 if self.selected_piece.color == Color.WHITE else 1
                            if (abs(cell[0] - prev_pos[0]) == 1 and 
                                cell[1] - prev_pos[1] == direction and
                                self.last_double_step_pawn and
                                self.last_double_step_pawn.position == (cell[0], prev_pos[1])):
                                
                                self.pieces.remove(self.last_double_step_pawn)
                                is_en_passant = True
                                is_capture = True

                        # Обычное взятие
                        for p in self.pieces[:]:
                            if p.position == cell and p.color != self.selected_piece.color:
                                self.pieces.remove(p)
                                is_capture = True
                                break

                        # Проверка на рокировку
                        if isinstance(self.selected_piece, King) and abs(cell[0] - prev_pos[0]) == 2:
                            is_castling = True
                            # Выполняем рокировку сразу после перемещения короля
                            self.selected_piece.do_castling_move(cell, self.pieces)


                        # Добавление хода в историю
                        self.add_move_to_history(prev_pos, cell, self.selected_piece, 
                                               is_capture, is_castling, is_en_passant)

                        # Перемещение фигуры
                        self.selected_piece.move_to(cell)

                        # Превращение пешки
                        if isinstance(self.selected_piece, Pawn):
                            last_rank = 0 if self.selected_piece.color == Color.WHITE else 7
                            if cell[1] == last_rank:
                                self.promotion_pawn = self.selected_piece
                                self.show_promotion_menu = True
                                self.selected_piece = None
                                self.show_selection = False
                                return True

                        # Обновление флага двойного хода пешки
                        if isinstance(self.selected_piece, Pawn) and abs(cell[1] - prev_pos[1]) == 2:
                            self.last_double_step_pawn = self.selected_piece
                        else:
                            self.last_double_step_pawn = None

                        if not self.promotion_pawn:
                            self.switch_turn()

                        self.selected_piece = None
                        self.show_selection = False
                    else:
                        self.selected_piece = None
                        self.show_selection = False
                else:
                    # Выбор фигуры
                    for piece in self.pieces:
                        if piece.position == cell and piece.color == self.current_turn:
                            self.selected_piece = piece
                            self.show_selection = True
                            break

        return True

    def promote_pawn(self, new_piece):
        if not self.promotion_pawn:
            return
            
        # Создаем новую фигуру на месте пешки
        promoted_piece = new_piece.__class__(
            self.screen,
            self.promotion_pawn.position,
            self.promotion_pawn.color
        )
        promoted_piece.parent_board = self
        
        # Удаляем пешку и добавляем новую фигуру
        self.pieces.remove(self.promotion_pawn)
        self.pieces.append(promoted_piece)
        
        # Сбрасываем флаги превращения
        self.promotion_pawn = None
        self.show_promotion_menu = False
        self.promotion_options = []
        self.promotion_rects = []
        
        # Передаем ход
        self.switch_turn()

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        text = "белые" if self.current_turn == Color.WHITE else "чёрные"
        self.turn_label = self.create_label(f"Ход: {text}", (COLS * TILE_SIZE + 20, 20))


    def is_draw_by_material(self):
        piece_types = {}
        kings = 0
        knights = 0
        bishops = []

        for piece in self.pieces:
            if isinstance(piece, King):
                kings += 1
            elif isinstance(piece, Knight):
                knights += 1
            elif isinstance(piece, Bishop):
                bishops.append(piece)
            else:
                return False

        if kings == 2 and knights == 0 and not bishops:
            return True
        elif kings == 2 and knights == 1 and not bishops:
            return True
        elif kings == 2 and not knights and len(bishops) == 1:
            return True
        elif kings == 2 and len(bishops) > 1 and not knights:
            same_color = bishops[0].position[0] % 2 == bishops[0].position[1] % 2
            for b in bishops[1:]:
                if b.position[0] % 2 != b.position[1] % 2 != same_color:
                    return False
            return True

        return False

    def get_current_move_number(self) -> int:
        return len(self.move_list) * 2 + (1 if self.current_turn == Color.WHITE else 0)

    def get_chess_notation(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                         piece: Piece, is_capture: bool, 
                         is_castling: bool = False, is_en_passant: bool = False) -> str:
        files = "abcdefgh"
        ranks = "87654321"
        from_sq = f"{files[from_pos[0]]}{ranks[from_pos[1]]}"
        to_sq = f"{files[to_pos[0]]}{ranks[to_pos[1]]}"

        if is_castling and isinstance(piece, King):
            return "0-0" if to_pos[0] > from_pos[0] else "0-0-0"

        symbol = "x" if is_capture or is_en_passant else "-"
        
        if isinstance(piece, Pawn):
            if is_en_passant:
                return f"{from_sq}{symbol}{to_sq} e.p."
            return f"{from_sq}{symbol}{to_sq}"
        
        piece_symbol = ""
        if isinstance(piece, Queen):
            piece_symbol = "Q"
        elif isinstance(piece, Rook):
            piece_symbol = "R"
        elif isinstance(piece, Bishop):
            piece_symbol = "B"
        elif isinstance(piece, Knight):
            piece_symbol = "N"
        elif isinstance(piece, King):
            piece_symbol = "K"
        
        return f"{piece_symbol}{symbol}{to_sq}"

    def add_move_to_history(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                          piece: Piece, is_capture: bool, 
                          is_castling: bool = False, is_en_passant: bool = False):
        move_number = self.get_current_move_number()
        notation = self.get_chess_notation(from_pos, to_pos, piece, is_capture, is_castling, is_en_passant)
        turn_prefix = "Белые" if self.current_turn == Color.WHITE else "Чёрные"
        full_move = f"{move_number}. {turn_prefix}: {notation}"

        if self.current_turn == Color.WHITE:
            self.move_list.append([full_move, ""])
        else:
            if self.move_list:
                self.move_list[-1][1] = full_move

    def show_promotion_ui(self):
        # TODO: Реализовать интерфейс превращения пешки
        pass

    def show_draw_popup(self, message: str):
        print(message)  # В реальной реализации можно использовать pygame для отображения

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    game = Board()
    game.run()