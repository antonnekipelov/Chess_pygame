import pygame
import copy

from bishop import Bishop
from colors import Color
from constants import *
from king import King
from knight import Knight
from pawn import Pawn
from queen import Queen
from rook import Rook
from vector import Vector2i


class Board:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((COLS * TILE_SIZE + 350, ROWS * TILE_SIZE + 100))
        pygame.display.set_caption("Chess Game")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)

        self.light_color = LIGHT_COLOR
        self.dark_color = DARK_COLOR
        self.is_game_over = False
        self.tiles = []
        self.pieces = []
        self.current_turn = Color.WHITE
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.selected_piece = None
        self.move_list = []
        self.move_history_stack = []

        self.undo_button_rect = pygame.Rect(COLS * TILE_SIZE + 20, 500, 120, 30)
        self.restart_button_rect = pygame.Rect(COLS * TILE_SIZE + 20, 540, 120, 30)

        self.create_board()
        self.add_pieces()

        self.selection_rect = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.selection_rect.fill(HIGHLIGHT_COLOR)
        self.show_selection = False

        self.turn_label = self.create_label("Ход: белые", (COLS * TILE_SIZE + 20, 20))
        self.move_history_label = self.create_label("История ходов:", (COLS * TILE_SIZE + 20, 60))

        self.promotion_pieces = []
        self.show_promotion = False
        self.history_scroll_offset = 0
        self.history_max_visible_lines = 20  # Количество видимых строк истории

    def create_board(self):
        self.tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                self.tiles.append((row, col, color))

    def add_pieces(self):
        self.pieces = []
        for i in range(8):
            self.pieces.append(Pawn(self.screen, Vector2i(i, 1), Color.BLACK))

        self.pieces += [
            Rook(self.screen, Vector2i(0, 0), Color.BLACK), Knight(self.screen, Vector2i(1, 0), Color.BLACK),
            Bishop(self.screen, Vector2i(2, 0), Color.BLACK), Queen(self.screen, Vector2i(3, 0), Color.BLACK),
            King(self.screen, Vector2i(4, 0), Color.BLACK), Bishop(self.screen, Vector2i(5, 0), Color.BLACK),
            Knight(self.screen, Vector2i(6, 0), Color.BLACK), Rook(self.screen, Vector2i(7, 0), Color.BLACK)
        ]

        for i in range(8):
            self.pieces.append(Pawn(self.screen, Vector2i(i, 6), Color.WHITE))

        self.pieces += [
            Rook(self.screen, Vector2i(0, 7), Color.WHITE), Knight(self.screen, Vector2i(1, 7), Color.WHITE),
            Bishop(self.screen, Vector2i(2, 7), Color.WHITE), Queen(self.screen, Vector2i(3, 7), Color.WHITE),
            King(self.screen, Vector2i(4, 7), Color.WHITE), Bishop(self.screen, Vector2i(5, 7), Color.WHITE),
            Knight(self.screen, Vector2i(6, 7), Color.WHITE), Rook(self.screen, Vector2i(7, 7), Color.WHITE)
        ]

    def create_label(self, text, pos):
        label = self.font.render(text, True, BLACK)
        return (label, pos)

    def draw(self):
        self.screen.fill((255, 255, 255))
        for row, col, color in self.tiles:
            pygame.draw.rect(self.screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        for piece in self.pieces:
            piece.draw()

        if self.show_selection and self.selected_piece:
            self.screen.blit(self.selection_rect, (self.selected_piece.position.x * TILE_SIZE, self.selected_piece.position.y * TILE_SIZE))

        self.screen.blit(self.turn_label[0], self.turn_label[1])
        for label, pos in getattr(self, 'move_history_labels', []):
            self.screen.blit(label, pos)

        pygame.draw.rect(self.screen, (220, 220, 220), self.undo_button_rect)
        pygame.draw.rect(self.screen, (220, 220, 220), self.restart_button_rect)
        self.screen.blit(self.font.render("Отменить ход", True, BLACK), (self.undo_button_rect.x + 5, self.undo_button_rect.y + 5))
        self.screen.blit(self.font.render("Новая игра", True, BLACK), (self.restart_button_rect.x + 5, self.restart_button_rect.y + 5))

        if self.show_promotion and self.promotion_pawn:
            self.draw_promotion_ui()
        
        # Рисуем индикатор прокрутки
        if len(self.move_list) > self.history_max_visible_lines:
            scroll_height = (self.history_max_visible_lines * 20) * (self.history_max_visible_lines / len(self.move_list))
            scroll_pos = (self.history_scroll_offset / len(self.move_list)) * (self.history_max_visible_lines * 20)
            pygame.draw.rect(
                self.screen, 
                (150, 150, 150), 
                (COLS * TILE_SIZE + 150, 60 + scroll_pos, 5, scroll_height)
            )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Обработка прокрутки истории ходов
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесо мыши вверх
                    self.history_scroll_offset = max(0, self.history_scroll_offset - 1)
                    self.update_move_history_label()
                elif event.button == 5:  # Колесо мыши вниз
                    self.history_scroll_offset = min(
                        max(0, len(self.move_list) - self.history_max_visible_lines), 
                        self.history_scroll_offset + 1
                    )
                    self.update_move_history_label()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()

                # Кнопка "Отменить ход"
                if self.undo_button_rect.collidepoint(mouse_pos):
                    self.undo_move()
                    continue

                # Кнопка "Новая игра"
                if self.restart_button_rect.collidepoint(mouse_pos):
                    self.restart_game()
                    continue

                if self.is_game_over:
                    continue

                # Обработка выбора клетки
                cell = Vector2i(mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

                # Обработка превращения пешки
                if self.show_promotion:
                    self.handle_promotion_click(mouse_pos)
                    continue

                # Если фигура уже выбрана
                if self.selected_piece:
                    if self.selected_piece.is_valid_move(cell, self.pieces):
                        self.move_piece(self.selected_piece, cell)
                    else:
                        self.selected_piece = None
                        self.show_selection = False
                else:
                    # Выбор новой фигуры
                    for piece in self.pieces:
                        if piece.position == cell and piece.color == self.current_turn:
                            self.selected_piece = piece
                            self.show_selection = True
                            break

        return True

    def move_piece(self, piece, target_pos):
        prev_pos = Vector2i(piece.position.x, piece.position.y)
        snapshot = [p.copy() for p in self.pieces]
        self.move_history_stack.append((piece.copy(), prev_pos, snapshot))

        # Проверка на рокировку
        is_castling = isinstance(piece, King) and abs(target_pos.x - piece.position.x) == 2

        # Удаляем фигуру, если это взятие (кроме рокировки)
        captured_piece = None
        if not is_castling:
            for p in self.pieces[:]:
                if p.position == target_pos and p.color != piece.color:
                    captured_piece = p
                    self.pieces.remove(p)
                    break

        # Перемещаем короля
        piece.move_to(target_pos)

        # Если это рокировка - перемещаем ладью
        if is_castling:
            direction = 1 if target_pos.x > piece.position.x else -1
            rook_x = 7 if direction > 0 else 0
            rook_new_x = 5 if direction > 0 else 3
            
            # Находим и перемещаем ладью
            for rook in [p for p in self.pieces if isinstance(p, Rook) and p.position.x == rook_x and p.position.y == target_pos.y]:
                rook.move_to(Vector2i(rook_new_x, target_pos.y))
                break

        # Формируем строку хода
        move_str = ""
        if is_castling:
            move_str = "O-O" if target_pos.x > prev_pos.x else "O-O-O"
        elif isinstance(piece, Pawn):
            if captured_piece:
                move_str = f"{chr(prev_pos.x + ord('a'))}x{chr(target_pos.x + ord('a'))}{8 - target_pos.y}"
            else:
                move_str = f"{chr(target_pos.x + ord('a'))}{8 - target_pos.y}"
        else:
            piece_letter = piece.__class__.__name__[0]
            if captured_piece:
                move_str = f"{piece_letter}x{chr(target_pos.x + ord('a'))}{8 - target_pos.y}"
            else:
                move_str = f"{piece_letter}{chr(target_pos.x + ord('a'))}{8 - target_pos.y}"

        if self.current_turn == Color.WHITE:
            self.move_list.append((move_str, ""))
        else:
            if self.move_list:
                self.move_list[-1] = (self.move_list[-1][0], move_str)

        self.update_move_history_label()
        self.switch_turn()
        self.selected_piece = None
        self.show_selection = False

    def switch_turn(self, reverse=False):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        turn_text = "белые" if self.current_turn == Color.WHITE else "чёрные"
        self.turn_label = self.create_label(f"Ход: {turn_text}", (COLS * TILE_SIZE + 20, 20))

    def undo_move(self):
        if self.move_history_stack:
            _, _, previous_pieces = self.move_history_stack.pop()
            self.pieces = [p.copy() for p in previous_pieces]
            
            # Удаляем последний ход из истории
            if self.current_turn == Color.WHITE:
                # Если сейчас ход белых, значит последний был черных
                if self.move_list and self.move_list[-1][1]:  # Если есть ход черных
                    white_move, _ = self.move_list[-1]
                    self.move_list[-1] = (white_move, "")  # Удаляем ход черных
                else:
                    # Иначе удаляем всю последнюю запись
                    self.move_list.pop()
            else:
                # Если сейчас ход черных, значит последний был белых
                if self.move_list:
                    self.move_list.pop()  # Удаляем последнюю пару ходов
            
            self.switch_turn(reverse=True)
            self.selected_piece = None
            self.show_selection = False
            self.update_move_history_label()

    def restart_game(self):
        self.add_pieces()
        self.selected_piece = None
        self.show_selection = False
        self.current_turn = Color.WHITE
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.show_promotion = False
        self.move_list = []
        self.move_history_stack = []
        self.update_move_history_label()

    def draw_promotion_ui(self):
        # implement if needed
        pass

    def handle_promotion_click(self, mouse_pos):
        pass

    def update_move_history_label(self):
        history_lines = ["История ходов:"]
        for i, (white_move, black_move) in enumerate(self.move_list):
            line = f"{i+1}. {white_move}"
            if black_move:
                line += f" - {black_move}"
            history_lines.append(line)

        # Ограничиваем количество отображаемых строк с учетом прокрутки
        start_idx = max(0, len(history_lines) - self.history_max_visible_lines - self.history_scroll_offset)
        visible_lines = history_lines[start_idx:start_idx + self.history_max_visible_lines]

        y_offset = 60
        self.move_history_labels = []
        for line in visible_lines:
            label = self.font.render(line, True, BLACK)
            self.move_history_labels.append((label, (COLS * TILE_SIZE + 20, y_offset)))
            y_offset += 20

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Board()
    game.run()
