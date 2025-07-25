import pygame

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
        self.screen = pygame.display.set_mode(
            (COLS * TILE_SIZE + 350, ROWS * TILE_SIZE + 100))
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
        self.move_stack = []

        self.create_board()
        self.add_pieces()

        self.selection_rect = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.selection_rect.fill(HIGHLIGHT_COLOR)
        self.show_selection = False

        self.turn_label = self.create_label("Ход: белые", (COLS * TILE_SIZE + 20, 20))
        self.move_history_label = self.create_label("История ходов:", (COLS * TILE_SIZE + 20, 60))

        self.promotion_pieces = []
        self.show_promotion = False
        self.halfmove_clock = 0

    def create_board(self):
        self.tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                self.tiles.append((row, col, color))

    def add_pieces(self):
        self.pieces = []

        for i in range(8):
            self.pieces.append(Pawn(self, Vector2i(i, 1), Color.BLACK))

        self.pieces.extend([
            Rook(self, Vector2i(0, 0), Color.BLACK),
            Knight(self, Vector2i(1, 0), Color.BLACK),
            Bishop(self, Vector2i(2, 0), Color.BLACK),
            Queen(self, Vector2i(3, 0), Color.BLACK),
            King(self, Vector2i(4, 0), Color.BLACK),
            Bishop(self, Vector2i(5, 0), Color.BLACK),
            Knight(self, Vector2i(6, 0), Color.BLACK),
            Rook(self, Vector2i(7, 0), Color.BLACK)
        ])

        for i in range(8):
            self.pieces.append(Pawn(self, Vector2i(i, 6), Color.WHITE))

        self.pieces.extend([
            Rook(self, Vector2i(0, 7), Color.WHITE),
            Knight(self, Vector2i(1, 7), Color.WHITE),
            Bishop(self, Vector2i(2, 7), Color.WHITE),
            Queen(self, Vector2i(3, 7), Color.WHITE),
            King(self, Vector2i(4, 7), Color.WHITE),
            Bishop(self, Vector2i(5, 7), Color.WHITE),
            Knight(self, Vector2i(6, 7), Color.WHITE),
            Rook(self, Vector2i(7, 7), Color.WHITE)
        ])

    def draw(self):
        self.screen.fill((255, 255, 255))
        for row, col, color in self.tiles:
            pygame.draw.rect(self.screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for i in range(COLS):
            label = self.font.render(letters[i], True, BLACK)
            self.screen.blit(label, (i * TILE_SIZE + TILE_SIZE // 2 - label.get_width() // 2, -20))
            self.screen.blit(label, (i * TILE_SIZE + TILE_SIZE // 2 - label.get_width() // 2, ROWS * TILE_SIZE + 10))

        for i in range(ROWS):
            label = self.font.render(str(ROWS - i), True, BLACK)
            self.screen.blit(label, (-20, i * TILE_SIZE + TILE_SIZE // 2 - label.get_height() // 2))
            self.screen.blit(label, (COLS * TILE_SIZE + 10, i * TILE_SIZE + TILE_SIZE // 2 - label.get_height() // 2))

        for piece in self.pieces:
            piece.draw(self.screen)

        if self.show_selection and self.selected_piece:
            self.screen.blit(self.selection_rect, (self.selected_piece.position.x * TILE_SIZE,
                                                   self.selected_piece.position.y * TILE_SIZE))

        self.screen.blit(self.turn_label[0], self.turn_label[1])
        for label, pos in getattr(self, 'move_history_labels', []):
            self.screen.blit(label, pos)

        if self.show_promotion and self.promotion_pawn:
            self.draw_promotion_ui()

        pygame.display.flip()

    def create_label(self, text, pos):
        label = self.font.render(text, True, BLACK)
        return (label, pos)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    self.undo_move()
                elif event.key == pygame.K_r:
                    self.restart_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_game_over:
                    continue

                mouse_pos = pygame.mouse.get_pos()
                cell = Vector2i(mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

                if self.show_promotion:
                    self.handle_promotion_click(mouse_pos)
                    continue

                if self.selected_piece:
                    if self.selected_piece.is_valid_move(cell, self.pieces):
                        self.move_piece(self.selected_piece, cell)
                    else:
                        self.selected_piece = None
                        self.show_selection = False
                else:
                    for piece in self.pieces:
                        if piece.position == cell and piece.color == self.current_turn:
                            self.selected_piece = piece
                            self.show_selection = True
                            break
        return True

    def move_piece(self, piece, target_pos):
        prev_pos = piece.position.copy()
        self.move_stack.append((piece, prev_pos.copy(), target_pos.copy(), self.pieces[:], self.current_turn))

        is_capture = False
        for p in self.pieces[:]:
            if p.position == target_pos and p.color != piece.color:
                is_capture = True
                self.pieces.remove(p)
                break

        is_castling = isinstance(piece, King) and abs(target_pos.x - prev_pos.x) == 2
        self.add_move_to_history(prev_pos, target_pos, piece, is_capture, is_castling)

        piece.move_to(target_pos)

        if piece.resets_fifty_move_counter(target_pos, self.pieces):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        if self.halfmove_clock >= 100:
            self.show_draw_popup("Ничья по правилу 50 ходов — не было взятий и ходов пешкой.")
            self.is_game_over = True
        if is_castling:
            piece.do_castling_move(target_pos, self.pieces)

        if isinstance(piece, Pawn):
            y_end = 0 if piece.color == Color.WHITE else 7
            if target_pos.y == y_end:
                self.promotion_pawn = piece
                self.show_promotion_ui()
                return

        self.last_double_step_pawn = None
        if isinstance(piece, Pawn) and abs(target_pos.y - prev_pos.y) == 2:
            self.last_double_step_pawn = piece

        if not self.promotion_pawn:
            self.switch_turn()
            if self.is_draw_by_material():
                self.is_game_over = True
                self.show_draw_popup("Ничья")

        self.selected_piece = None
        self.show_selection = False

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        turn_text = "белые" if self.current_turn == Color.WHITE else "чёрные"
        self.turn_label = self.create_label(f"Ход: {turn_text}", (COLS * TILE_SIZE + 20, 20))

    def undo_move(self):
        if not self.move_stack:
            return
        piece, old_pos, new_pos, pieces_before, prev_turn = self.move_stack.pop()
        piece.position = old_pos
        self.pieces = [p for p in pieces_before]
        self.current_turn = prev_turn
        self.selected_piece = None
        self.show_selection = False
        if self.move_list:
            if self.current_turn == Color.WHITE:
                self.move_list.pop()
            else:
                self.move_list[-1][1] = ""
        self.update_move_history_label()

    def restart_game(self):
        self.pieces.clear()
        self.move_list.clear()
        self.move_stack.clear()
        self.selected_piece = None
        self.show_selection = False
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.current_turn = Color.WHITE
        self.turn_label = self.create_label("Ход: белые", (COLS * TILE_SIZE + 20, 20))
        self.move_history_labels = []
        self.add_pieces()

    def show_promotion_ui(self):
        self.show_promotion = True
        self.promotion_pieces = []

        screen_width, screen_height = self.screen.get_size()
        total_width = TILE_SIZE * 4
        x_start = (screen_width - total_width) // 2
        y_start = (screen_height - TILE_SIZE) // 2

        pieces = [Queen, Rook, Bishop, Knight]
        for i, piece_type in enumerate(pieces):
            piece = piece_type(self, Vector2i(0, 0), self.promotion_pawn.color)
            pos = (x_start + i * TILE_SIZE, y_start)
            self.promotion_pieces.append(
                (piece, pos))

    def draw_promotion_ui(self):
        for piece, pos in self.promotion_pieces:
            rect = pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
            piece_image = piece.get_image()
            self.screen.blit(piece_image, pos)

    def handle_promotion_click(self, mouse_pos):
        for piece, (x, y) in self.promotion_pieces:
            if x <= mouse_pos[0] < x + TILE_SIZE and y <= mouse_pos[1] < y + TILE_SIZE:
                self.promote_to(type(piece))
                break

    def promote_to(self, piece_type):
        if self.promotion_pawn:
            new_piece = piece_type(
                self, self.promotion_pawn.position, self.promotion_pawn.color)
            self.pieces.remove(self.promotion_pawn)
            self.pieces.append(new_piece)
            self.promotion_pawn = None
            self.show_promotion = False
            self.switch_turn()

    def add_move_to_history(self, from_pos, to_pos, piece, is_capture, is_castling):
        notation = self.get_chess_notation(
            from_pos, to_pos, piece, is_capture, is_castling)
        # turn_prefix = "Белые" if self.current_turn == Color.WHITE else "Чёрные"
        full_move = notation

        if self.current_turn == Color.WHITE:
            self.move_list.append([full_move, ""])
        else:
            if self.move_list:
                self.move_list[-1][1] = full_move

        self.update_move_history_label()

    def update_move_history_label(self):
        history_lines = ["История ходов:"]
        
        for i, (white_move, black_move) in enumerate(self.move_list):
            line = f"{i+1}. {white_move}"
            if black_move:
                line += f" - {black_move}"
            history_lines.append(line)
        
        # Объединяем все строки с переносами
        history_text = "\n".join(history_lines)
        
        # Разбиваем текст на строки, если они слишком длинные
        wrapped_lines = []
        for line in history_lines:
            # Если строка слишком длинная, разбиваем её
            if len(line) > 50:  # Максимальная длина строки
                parts = []
                current_part = ""
                for word in line.split():
                    if len(current_part) + len(word) + 1 <= 50:
                        current_part += " " + word if current_part else word
                    else:
                        parts.append(current_part)
                        current_part = word
                if current_part:
                    parts.append(current_part)
                wrapped_lines.extend(parts)
            else:
                wrapped_lines.append(line)
        
        # Рендерим каждую строку отдельно
        y_offset = 60
        self.move_history_labels = []
        for line in wrapped_lines:
            label = self.font.render(line, True, BLACK)
            self.move_history_labels.append((label, (COLS * TILE_SIZE + 20, y_offset)))
            y_offset += 20  # Отступ между строками

    def get_chess_notation(self, from_pos, to_pos, piece, is_capture, is_castling):
        files = "abcdefgh"
        ranks = "87654321"
        from_sq = f"{files[from_pos.x]}{ranks[from_pos.y]}"
        to_sq = f"{files[to_pos.x]}{ranks[to_pos.y]}"

        if is_castling and isinstance(piece, King):
            return "0-0" if to_pos.x > from_pos.x else "0-0-0"

        symbol = 'x' if is_capture else '→'

        if isinstance(piece, Pawn):
            return f"{from_sq}{symbol}{to_sq}"

        piece_name = ""
        if isinstance(piece, Queen):
            piece_name = "Ферзь"
        elif isinstance(piece, Rook):
            piece_name = "Ладья"
        elif isinstance(piece, Bishop):
            piece_name = "Слон"
        elif isinstance(piece, Knight):
            piece_name = "Конь"
        elif isinstance(piece, King):
            piece_name = "Король"

        return f"{piece_name} ({from_sq}{symbol}{to_sq})"

    def is_draw_by_material(self):
        piece_types = set()
        kings = 0
        knights = 0

        for piece in self.pieces:
            if isinstance(piece, King):
                kings += 1
            elif isinstance(piece, Knight):
                knights += 1
            else:
                # Any other piece means mate is possible
                return False

        if kings == 2 and knights == 0:
            self.show_draw_popup("Ничья: остались только короли.")
            return True
        elif kings == 2 and knights == 1:
            self.show_draw_popup(
                "Ничья: только короли и один конь — мат невозможен.")
            return True

        return False

    def show_draw_popup(self, message):
        # In a real implementation, you'd show a proper popup
        print(message)  # Simplified for this example

    def is_draw_by_fifty_move_rule(self) -> bool:
        return self.halfmove_clock >= 100	

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
