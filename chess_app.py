from chess_app import ChessApp
import pygame
import sys
from board import Board


class ChessApp:
    def __init__(self):
        pygame.init()
        self.TILE_SIZE = 64
        self.board_size = 8
        self.screen_width = self.board_size * self.TILE_SIZE + 200  # +200 для UI
        self.screen_height = self.board_size * self.TILE_SIZE + 100
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Шахматы")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # Инициализация игровых компонентов
        self.board = Board()
        self.ui_panel = UIPanel(self)
        self.game_state = "menu"  # menu/game/promotion/game_over

        # Цвета
        self.colors = {
            "light": pygame.Color(240, 217, 181),
            "dark": pygame.Color(181, 136, 99),
            "highlight": pygame.Color(0, 128, 255, 76),
            "text": pygame.Color(255, 255, 255),
            "panel": pygame.Color(50, 50, 50)
        }

    def run(self):
        """Главный игровой цикл"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.game_state == "game":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # ЛКМ
                        self.board.handle_click(event.pos)

            # Обработка UI событий
            self.ui_panel.handle_event(event)

    def update(self):
        """Обновление состояния игры"""
        if self.game_state == "game":
            self.board.update()

    def draw(self):
        """Отрисовка всех компонентов"""
        self.screen.fill(pygame.Color(30, 30, 30))

        # Отрисовка доски
        board_surface = pygame.Surface((self.board_size * self.TILE_SIZE,
                                        self.board_size * self.TILE_SIZE))
        self.board.draw(board_surface)
        self.screen.blit(board_surface, (0, 0))

        # Отрисовка UI
        self.ui_panel.draw(self.screen)

        # Отрисовка попапов
        if self.game_state == "promotion":
            self.draw_promotion_popup()
        elif self.game_state == "game_over":
            self.draw_game_over_popup()

        pygame.display.flip()

    def draw_promotion_popup(self):
        """Отрисовка попапа превращения пешки"""
        popup_rect = pygame.Rect(
            self.screen_width // 2 - 150,
            self.screen_height // 2 - 100,
            300, 200
        )
        pygame.draw.rect(self.screen, self.colors["panel"], popup_rect)
        pygame.draw.rect(self.screen, pygame.Color("white"), popup_rect, 2)

        title = self.font.render("Выберите фигуру:", True, self.colors["text"])
        self.screen.blit(title, (popup_rect.centerx - title.get_width()//2,
                                 popup_rect.y + 20))

        # Кнопки выбора фигур
        pieces = ["Queen", "Rook", "Bishop", "Knight"]
        for i, piece in enumerate(pieces):
            btn_rect = pygame.Rect(
                popup_rect.x + 20 + i * 70,
                popup_rect.y + 60,
                60, 40
            )
            pygame.draw.rect(self.screen, self.colors["light"], btn_rect)
            text = self.font.render(piece[0], True, pygame.Color("black"))
            self.screen.blit(text, (btn_rect.centerx - text.get_width()//2,
                                    btn_rect.centery - text.get_height()//2))

    def start_new_game(self):
        """Начинает новую игру"""
        self.board.new_game()
        self.game_state = "game"

    import pygame


class UIPanel:
    def __init__(self, app):
        self.app = app
        self.buttons = {
            "new_game": pygame.Rect(
                app.board_size * app.TILE_SIZE + 20, 20, 160, 40
            )
        }

    def draw(self, surface):
        """Отрисовка UI панели"""
        panel_rect = pygame.Rect(
            self.app.board_size * self.app.TILE_SIZE, 0,
            200, self.app.screen_height
        )
        pygame.draw.rect(surface, self.app.colors["panel"], panel_rect)

        # Кнопка новой игры
        pygame.draw.rect(
            surface, self.app.colors["light"], self.buttons["new_game"])
        text = self.app.font.render("Новая игра", True, pygame.Color("black"))
        surface.blit(text, (
            self.buttons["new_game"].centerx - text.get_width()//2,
            self.buttons["new_game"].centery - text.get_height()//2
        ))

        # История ходов
        moves_text = self.app.font.render(
            "История ходов:", True, self.app.colors["text"])
        surface.blit(moves_text, (panel_rect.x + 10, 80))

        # Текущий ход
        turn_text = self.app.font.render(
            f"Ход: {'белые' if self.app.board.current_turn == 'white' else 'чёрные'}",
            True, self.app.colors["text"]
        )
        surface.blit(turn_text, (panel_rect.x + 10, panel_rect.height - 40))

    def handle_event(self, event):
        """Обработка событий UI"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons["new_game"].collidepoint(event.pos):
                self.app.start_new_game()


if __name__ == "__main__":
    app = ChessApp()
    app.run()
