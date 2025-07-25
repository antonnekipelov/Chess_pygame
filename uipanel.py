import pygame

from chess_app import ChessApp

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
        pygame.draw.rect(surface, self.app.colors["light"], self.buttons["new_game"])
        text = self.app.font.render("Новая игра", True, pygame.Color("black"))
        surface.blit(text, (
            self.buttons["new_game"].centerx - text.get_width()//2,
            self.buttons["new_game"].centery - text.get_height()//2
        ))
        
        # История ходов
        moves_text = self.app.font.render("История ходов:", True, self.app.colors["text"])
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