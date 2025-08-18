import pygame
from typing import List, Tuple
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
        self.screen = pygame.display.set_mode(
            (COLS * TILE_SIZE + 300, ROWS * TILE_SIZE+80))
        pygame.display.set_caption("Шахматы")

        self.pieces = []
        self.current_turn = Color.WHITE
        self.selected_piece = None
        self.show_selection = False
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.halfmove_clock = 0
        self.is_game_over = False
        self.move_list = []
        self.promotion_options = []  # Для хранения вариантов превращения

        self.selection_rect = pygame.Surface(
            (TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.selection_rect.fill((0, 128, 255, 80))

        self.font = pygame.font.SysFont('Arial', 16)
        self.turn_label = self.create_label(
            "Ход: белые", (COLS * TILE_SIZE + 20, 20))

        # Параметры для истории ходов с полосой прокрутки
        self.move_history_rect = pygame.Rect(
            COLS * TILE_SIZE + 10, 50, 280, ROWS * TILE_SIZE - 60)
        self.move_history_font = pygame.font.SysFont('Arial', 14)
        self.move_history_surface = pygame.Surface(
            (280, ROWS * TILE_SIZE - 60))
        self.scroll_y = 0  # Текущая позиция прокрутки
        self.scroll_bar_rect = pygame.Rect(
            COLS * TILE_SIZE + 280, 50, 10, ROWS * TILE_SIZE - 60)  # Полоса прокрутки
        self.scroll_thumb_rect = pygame.Rect(
            COLS * TILE_SIZE + 280, 50, 10, 50)  # Бегунок прокрутки
        self.scroll_dragging = False  # Флаг перетаскивания бегунка
        self.scroll_start_y = 0  # Начальная позиция при перетаскивании
        self.content_height = 0  # Общая высота содержимого

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
        back_row_black = [Rook, Knight, Bishop,
                          Queen, King, Bishop, Knight, Rook]
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
        back_row_white = [Rook, Knight, Bishop,
                          Queen, King, Bishop, Knight, Rook]
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
            pygame.draw.rect(self.screen, color, (col * TILE_SIZE,
                             row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Рисуем фигуры
        for piece in self.pieces:
            piece.draw()

        # Рисуем выделение выбранной фигуры
        if self.show_selection and self.selected_piece:
            x = self.selected_piece.position[0] * TILE_SIZE
            y = self.selected_piece.position[1] * TILE_SIZE
            self.screen.blit(self.selection_rect, (x, y))

        # Рисуем меню превращения
        if self.promotion_pawn:
            self.draw_promotion_menu()

        # Рисуем метку текущего хода
        self.screen.blit(self.turn_label[0], self.turn_label[1])

        # Рисуем историю ходов
        self.draw_move_history()

        # Рисуем результат игры, если игра завершена
        if self.is_game_over and hasattr(self, 'game_result'):
            self.draw_game_result()
        else:
           # Кнопка "Сдаться", если игра не окончена
            button_width, button_height = 200, 40
            button_x = COLS * TILE_SIZE + 50
            # ставим под историей ходов, отталкиваясь от низа панели
            button_y = self.move_history_rect.bottom + 20  
            self.resign_button = pygame.Rect(button_x, button_y, button_width, button_height)

            pygame.draw.rect(self.screen, (200, 100, 100), self.resign_button, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), self.resign_button, 2, border_radius=5)

            button_font = pygame.font.SysFont('Arial', 22, bold=True)
            button_text = button_font.render("Сдаться", True, (0, 0, 0))
            self.screen.blit(
                button_text,
                (button_x + (button_width - button_text.get_width()) // 2,
                 button_y + (button_height - button_text.get_height()) // 2)
            )

        pygame.display.flip()


    def draw_promotion_menu(self):
        if not self.promotion_pawn:
            return

        # Полупрозрачный фон
        overlay = pygame.Surface(
            (COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Параметры панели выбора
        panel_width = TILE_SIZE * 4
        panel_height = TILE_SIZE
        panel_x = (COLS * TILE_SIZE - panel_width) // 2  # Центр доски по X
        panel_y = (ROWS * TILE_SIZE - panel_height) // 2  # Центр доски по Y

        # Рисуем панель
        pygame.draw.rect(self.screen, (240, 217, 181),
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (181, 136, 99),
                         (panel_x, panel_y, panel_width, panel_height), 2)

        # Варианты превращения
        choices = [Queen, Rook, Bishop, Knight]
        self.promotion_options = []

        for i, piece_cls in enumerate(choices):
            x = panel_x + i * TILE_SIZE
            piece = piece_cls(self.screen, (0, 0), self.promotion_pawn.color)
            piece.parent_board = self

            # Рисуем фигуру
            if piece.sprite:
                self.screen.blit(piece.sprite, (x, panel_y))
            else:
                # Fallback если нет спрайта
                color = (255, 255, 255) if piece.color == Color.WHITE else (
                    0, 0, 0)
                pygame.draw.rect(self.screen, color,
                                 (x, panel_y, TILE_SIZE, TILE_SIZE))

            # Сохраняем прямоугольники для обработки кликов
            self.promotion_options.append(
                (piece, pygame.Rect(x, panel_y, TILE_SIZE, TILE_SIZE)))

    def handle_promotion_choice(self, mouse_pos):
        for piece, rect in self.promotion_options:
            if rect.collidepoint(mouse_pos):
                # Определяем символ фигуры для превращения
                prom_letter = ""
                if isinstance(piece, Queen):
                    prom_letter = "Q"
                elif isinstance(piece, Rook):
                    prom_letter = "R"
                elif isinstance(piece, Bishop):
                    prom_letter = "B"
                elif isinstance(piece, Knight):
                    prom_letter = "N"

                # Получаем координаты превращения
                files = "abcdefgh"
                ranks = "12345678"
                pos = self.promotion_pawn.position
                to_file = files[pos[0]]
                to_rank = ranks[pos[1]]

                # Формируем запись хода
                move = ""
                if self.promotion_pawn.captured_piece:  # Превращение с взятием
                    # Берем исходную позицию пешки ДО хода
                    from_file = files[self.promotion_pawn.prev_position[0]]
                    move = f"{from_file}x{to_file}{to_rank}={prom_letter}"
                else:  # Обычное превращение
                    move = f"{to_file}{to_rank}={prom_letter}"

                # Добавляем ход в историю
                if self.current_turn == Color.WHITE:
                    move_num = len(self.move_list) + 1
                    self.move_list.append(f"{move_num}. {move}")
                else:
                    if self.move_list:
                        self.move_list[-1] += f" {move}"
                    else:
                        self.move_list.append(f"1... {move}")

                # Создаем новую фигуру
                new_piece = piece.__class__(
                    self.screen, self.promotion_pawn.position, self.promotion_pawn.color)
                new_piece.parent_board = self

                # Заменяем пешку
                self.pieces.remove(self.promotion_pawn)
                self.pieces.append(new_piece)

                # Сбрасываем состояние превращения
                self.promotion_pawn = None
                self.promotion_options = []

                # Передаем ход
                self.switch_turn()
                return True
        return False

    def handle_events(self):
        """Обработка событий, включая прокрутку и ничейные ситуации"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Обработка клика по кнопке Новая игра
            if self.is_game_over and hasattr(self, 'new_game_button'):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.new_game_button.collidepoint(event.pos):
                        self.reset_game()
                        continue

            # Клик по кнопке "Сдаться"
            if not self.is_game_over and hasattr(self, 'resign_button'):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.resign_button.collidepoint(event.pos):
                        self.resign()
                        continue

            # Если игра завершена, обрабатываем только закрытие окна и новую игру
            if self.is_game_over:
                continue

            # Прокрутка колесом мыши
            if event.type == pygame.MOUSEWHEEL:
                max_scroll = max(0, self.content_height - (ROWS * TILE_SIZE - 60))
                self.scroll_y = max(0, min(max_scroll, self.scroll_y - event.y * 20))

            # Начало перетаскивания бегунка
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.scroll_thumb_rect.collidepoint(event.pos):
                    self.scroll_dragging = True
                    self.scroll_start_y = event.pos[1] - self.scroll_thumb_rect.y

            # Конец перетаскивания
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.scroll_dragging = False

            # Перетаскивание бегунка
            if event.type == pygame.MOUSEMOTION and self.scroll_dragging:
                max_scroll = max(0, self.content_height - (ROWS * TILE_SIZE - 60))
                if max_scroll > 0:
                    new_y = event.pos[1] - self.scroll_start_y
                    new_y = max(50, min(new_y, 50 + (ROWS * TILE_SIZE - 60) - self.scroll_thumb_rect.height))

                    scroll_ratio = (new_y - 50) / ((ROWS * TILE_SIZE - 60) - self.scroll_thumb_rect.height)
                    self.scroll_y = scroll_ratio * max_scroll

            # Обработка превращения пешки
            if self.promotion_pawn:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_promotion_choice(pygame.mouse.get_pos())
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Игнорируем клики на полосе прокрутки
                if COLS * TILE_SIZE + 280 <= event.pos[0] <= COLS * TILE_SIZE + 290:
                    continue

                mouse_pos = pygame.mouse.get_pos()
                cell = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

                if self.selected_piece:
                    legal_moves = self.get_legal_moves(self.selected_piece)
                    if cell in legal_moves:
                        prev_pos = self.selected_piece.position
                        is_capture = False
                        is_castling = False
                        is_en_passant = False
                        captured_piece = None
                        is_pawn_move = isinstance(self.selected_piece, Pawn)

                        # Взятие на проходе
                        if isinstance(self.selected_piece, Pawn):
                            direction = -1 if self.selected_piece.color == Color.WHITE else 1
                            if (abs(cell[0] - prev_pos[0]) == 1 and 
                                cell[1] - prev_pos[1] == direction and
                                self.last_double_step_pawn and
                                self.last_double_step_pawn.position == (cell[0], prev_pos[1])):

                                captured_piece = self.last_double_step_pawn
                                self.pieces.remove(self.last_double_step_pawn)
                                is_en_passant = True
                                is_capture = True
                                self.halfmove_clock = 0  # Сброс при взятии

                        # Обычное взятие
                        for p in self.pieces[:]:
                            if p.position == cell and p.color != self.selected_piece.color:
                                captured_piece = p
                                is_capture = True
                                self.halfmove_clock = 0  # Сброс при взятии
                                break

                        # Проверка на рокировку
                        if isinstance(self.selected_piece, King) and abs(cell[0] - prev_pos[0]) == 2:
                            is_castling = True
                            self.selected_piece.do_castling_move(cell, self.pieces)

                        # Превращение пешки
                        if isinstance(self.selected_piece, Pawn):
                            last_rank = 0 if self.selected_piece.color == Color.WHITE else 7
                            if cell[1] == last_rank:
                                # Сначала перемещаем пешку на конечную клетку
                                self.selected_piece.move_to(cell)

                                # Удаляем взятую фигуру (если было взятие)
                                if is_capture and captured_piece in self.pieces:
                                    self.pieces.remove(captured_piece)

                                # Устанавливаем пешку для превращения
                                self.promotion_pawn = self.selected_piece
                                self.promotion_pawn.captured_piece = captured_piece if is_capture else None
                                self.selected_piece = None
                                self.show_selection = False
                                self.halfmove_clock = 0  # Сброс при превращении пешки
                                return True

                        # Добавляем ход в историю (если не превращение)
                        if not (isinstance(self.selected_piece, Pawn) and cell[1] in (0, 7)):
                            self.add_move_to_history(prev_pos, cell, self.selected_piece, 
                                                is_capture, is_castling, is_en_passant)

                        # Перемещение фигуры
                        self.selected_piece.move_to(cell)

                        # Удаляем взятые фигуры после перемещения (кроме случая превращения)
                        if is_capture and captured_piece and captured_piece in self.pieces:
                            self.pieces.remove(captured_piece)

                        # Обновление счетчика 50 ходов
                        if is_capture or is_pawn_move:
                            self.halfmove_clock = 0  # Сброс при взятии или ходе пешкой
                        else:
                            self.halfmove_clock += 1  # Увеличение счетчика

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

        # Проверка ничейных ситуаций после каждого хода
        if not self.is_game_over:
            self.is_draw_by_material(self.pieces)
            self.check_fifty_move_rule()

        return True


    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        text = "белые" if self.current_turn == Color.WHITE else "чёрные"
        self.turn_label = self.create_label(
            f"Ход: {text}", (COLS * TILE_SIZE + 20, 20))

    def add_move_to_history(self, from_pos, to_pos, piece, is_capture, is_castling=False, is_en_passant=False, promotion=None):
        files = "abcdefgh"
        ranks = "12345678"

        piece_letters = {
            Knight: 'N',
            Bishop: 'B',
            Rook: 'R',
            Queen: 'Q',
            King: 'K',
            Pawn: ''
        }

        piece_letter = piece_letters.get(type(piece), '')
        from_file = files[from_pos[0]]
        from_rank = ranks[from_pos[1]]
        to_file = files[to_pos[0]]
        to_rank = ranks[to_pos[1]]

        if is_castling:
            move = "O-O" if to_pos[0] > from_pos[0] else "O-O-O"
        else:
            move = ""
            if isinstance(piece, Pawn):
                # Для пешки указываем только файл при взятии
                if is_capture:
                    move += f"{from_file}x"
                move += f"{to_file}{to_rank}"
            else:
                # Для других фигур
                if is_capture:
                    # Указываем только тип фигуры, знак взятия и поле
                    move += f"{piece_letter}x{to_file}{to_rank}"
                else:
                    move += f"{piece_letter}{to_file}{to_rank}"

            if promotion:
                move += f"={promotion}"

        # Всегда создаем новую запись для хода белых
        if self.current_turn == Color.WHITE:
            move_num = len(self.move_list) + 1
            self.move_list.append(f"{move_num}. {move}")
        else:
            # Добавляем ход черных к последней записи
            if self.move_list:
                self.move_list[-1] += f" {move}"
            else:
                # На случай если черные ходят первыми (не должно быть)
                self.move_list.append(f"1... {move}")

    def draw_move_history(self):
        """Отрисовка истории ходов с полосой прокрутки и фиксированным заголовком"""
        # Очищаем поверхность
        self.move_history_surface.fill((240, 240, 240))
        pygame.draw.rect(self.move_history_surface, (200, 200,
                         200), (0, 0, 280, ROWS * TILE_SIZE - 60), 2)

        # Отрисовка ходов с учетом прокрутки
        y_offset = 40 - self.scroll_y
        column_width = 120

        # Вычисляем общую высоту содержимого
        self.content_height = 40 + len(self.move_list) * 20

        # Отрисовываем только видимые ходы
        for move in self.move_list:
            parts = move.split(' ')
            if len(parts) >= 2:
                # Ход белых
                white_part = f"{parts[0]} {parts[1]}"
                white_text = self.move_history_font.render(
                    white_part, True, (0, 0, 0))
                if 0 <= y_offset < ROWS * TILE_SIZE - 70:  # Проверка видимости
                    self.move_history_surface.blit(white_text, (10, y_offset))

                # Ход черных (если есть)
                if len(parts) >= 3:
                    black_text = self.move_history_font.render(
                        parts[2], True, (0, 0, 0))
                    if 0 <= y_offset < ROWS * TILE_SIZE - 70:  # Проверка видимости
                        self.move_history_surface.blit(
                            black_text, (10 + column_width, y_offset))
            y_offset += 20

        # Отображаем поверхность с историей ходов
        self.screen.blit(self.move_history_surface,
                         (COLS * TILE_SIZE + 10, 50))

        # Отрисовываем заголовок НАД поверхностью с прокруткой (фиксированная позиция)
        title = self.move_history_font.render(
            "История ходов:", True, (0, 0, 0))
        self.screen.blit(title, (COLS * TILE_SIZE + 20, 50))

        # Отрисовка полосы прокрутки
        pygame.draw.rect(self.screen, (220, 220, 220), self.scroll_bar_rect)

        # Вычисление размера и позиции бегунка
        visible_ratio = min(1.0, (ROWS * TILE_SIZE - 60) /
                            max(1, self.content_height))
        thumb_height = max(20, (ROWS * TILE_SIZE - 60) * visible_ratio)
        max_scroll = max(0, self.content_height - (ROWS * TILE_SIZE - 60))
        thumb_position = 50 + (self.scroll_y / max_scroll) * \
            ((ROWS * TILE_SIZE - 60) - thumb_height) if max_scroll > 0 else 50

        self.scroll_thumb_rect = pygame.Rect(
            COLS * TILE_SIZE + 280, thumb_position, 10, thumb_height)
        pygame.draw.rect(self.screen, (150, 150, 150), self.scroll_thumb_rect)

    def is_draw_by_material(self, pieces) -> bool:

        kings = 0
        knights = 0
        bishops = []

        for piece in pieces:
            if isinstance(piece, King):
                kings += 1
            elif isinstance(piece, Knight):
                knights += 1
            elif isinstance(piece, Bishop):
                bishops.append(piece)
            else:
                # Любая другая фигура — мат возможен
                return False

        # Только короли
        if kings == 2 and knights == 0 and len(bishops) == 0:
            self.set_draw("Ничья: остались только короли.")
            return True

        # Только короли и один конь
        elif kings == 2 and knights == 1 and len(bishops) == 0:
            self.set_draw("Ничья: только короли и один конь — мат невозможен.")
            return True

        # Только короли и один слон
        elif kings == 2 and knights == 0 and len(bishops) == 1:
            self.set_draw("Ничья: только короли и один слон — мат невозможен.")
            return True

        # Только короли и несколько слонов
        elif kings == 2 and knights == 0 and len(bishops) > 1:
            same_color = bishops[0].is_dark_square()
            for b in bishops[1:]:
                if b.is_dark_square() != same_color:
                    # Есть слоны на разных цветах — мат возможен
                    return False
            # Все слоны одного цвета — ничья
            self.set_draw("Ничья: только короли и однопольные слоны — мат невозможен.")
            return True

        return False


    def set_draw(self, reason):
        """Устанавливает ничью с указанной причиной"""
        self.game_result = "1/2-1/2"
        self.game_result_reason = reason
        self.is_game_over = True
        # Обновляем интерфейс
        self.draw()
        pygame.display.flip()

    def add_draw_to_history(self):
        """Добавляет запись о ничьей в историю ходов"""
        if self.current_turn == Color.WHITE:
            if self.move_list:
                self.move_list[-1] += " 1/2-1/2"
            else:
                self.move_list.append("1/2-1/2")
        else:
            self.move_list.append(f"{len(self.move_list) + 1}. 1/2-1/2")

    def draw_game_result(self):
        """Отрисовка результата игры с кнопкой Новая игра"""
        overlay = pygame.Surface(
            (COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_width = 400
        panel_height = 180
        panel_x = (COLS * TILE_SIZE - panel_width) // 2
        panel_y = (ROWS * TILE_SIZE - panel_height) // 2

        # Рисуем панель
        pygame.draw.rect(self.screen, (240, 217, 181),
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (181, 136, 99),
                         (panel_x, panel_y, panel_width, panel_height), 3)

        # Шрифты
        font_large = pygame.font.SysFont('Arial', 36, bold=True)
        font_small = pygame.font.SysFont('Arial', 18)
        font_button = pygame.font.SysFont('Arial', 24, bold=True)

        # Текст результата
        result_text = font_large.render(self.game_result, True, (0, 0, 0))
        reason_text = font_small.render(
            self.game_result_reason, True, (0, 0, 0))

        # Кнопка Новая игра
        button_width, button_height = 200, 40
        button_x = panel_x + (panel_width - button_width) // 2
        button_y = panel_y + panel_height - button_height - 20
        self.new_game_button = pygame.Rect(
            button_x, button_y, button_width, button_height)

        pygame.draw.rect(self.screen, (118, 150, 86),
                         self.new_game_button, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0),
                         self.new_game_button, 2, border_radius=5)

        button_text = font_button.render("Новая игра", True, (0, 0, 0))
        self.screen.blit(button_text,
                         (button_x + (button_width - button_text.get_width()) // 2,
                          button_y + (button_height - button_text.get_height()) // 2))

        # Позиционирование текста
        self.screen.blit(result_text,
                         (panel_x + (panel_width - result_text.get_width()) // 2,
                          panel_y + 20))
        self.screen.blit(reason_text,
                         (panel_x + (panel_width - reason_text.get_width()) // 2,
                          panel_y + 70))

    def reset_game(self):
        """Сбрасывает игру в начальное состояние"""
        # Сбрасываем все игровые параметры
        self.pieces = []
        self.current_turn = Color.WHITE
        self.selected_piece = None
        self.show_selection = False
        self.last_double_step_pawn = None
        self.promotion_pawn = None
        self.halfmove_clock = 0
        self.is_game_over = False
        self.move_list = []
        self.promotion_options = []
        self.game_result = None
        self.game_result_reason = ""
        self.scroll_y = 0

        # Обновляем метку хода
        self.turn_label = self.create_label(
            "Ход: белые", (COLS * TILE_SIZE + 20, 20))

        # Пересоздаем доску и фигуры
        self.create_board()
        self.add_pieces()

        # Перерисовываем экран
        self.draw()

    def check_fifty_move_rule(self):
        """Проверяет ничью по правилу 50 ходов"""
        if self.halfmove_clock >= 100:  # 50 ходов = 100 полуходов
            self.set_draw("Ничья по правилу 50 ходов")
            return True
        return False
    
    def resign(self):
        """Игрок сдаётся, партия завершается поражением"""
        if self.current_turn == Color.WHITE:
            self.game_result = "0-1"
            self.game_result_reason = "Белые сдались"
        else:
            self.game_result = "1-0"
            self.game_result_reason = "Чёрные сдались"
        self.is_game_over = True
        self.draw()
        pygame.display.flip()

    def is_in_check(self, color):
        """Проверяет, находится ли король данного цвета под шахом"""
        king = next((p for p in self.pieces if isinstance(p, King) and p.color == color), None)
        if not king:
            return False

        king_pos = king.position
        for piece in self.pieces:
            if piece.color != color:
                if piece.is_valid_move(king_pos, self.pieces):
                    return True
        return False

    def get_legal_moves(self, piece):
        """Возвращает список ходов фигуры, которые не оставляют своего короля под шахом"""
        legal_moves = []
        # Перебираем все клетки доски
        for x in range(8):
            for y in range(8):
                move = (x, y)
                if piece.is_valid_move(move, self.pieces):
                    original_pos = piece.position
                    captured_piece = next((p for p in self.pieces if p.position == move and p.color != piece.color), None)

                    # временно выполняем ход
                    piece.position = move
                    if captured_piece:
                        self.pieces.remove(captured_piece)

                    # проверяем шах
                    if not self.is_in_check(piece.color):
                        legal_moves.append(move)

                    # откат
                    piece.position = original_pos
                    if captured_piece:
                        self.pieces.append(captured_piece)

        return legal_moves



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
