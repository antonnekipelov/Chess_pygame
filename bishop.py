from colors import Color
from piece import Piece
from vector import Vector2i


class Bishop(Piece):
    def __init__(self, parent_node, pos: Vector2i, clr: str):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}B.png"
        super().__init__(parent_node, pos, clr, texture_path)
    
    def is_valid_move(self, target: Vector2i, pieces: list, ignore_checks=False) -> bool:
        # Сначала базовая проверка (нельзя бить свои фигуры)
        if not super().is_valid_move(target, pieces, ignore_checks):
            return False

        dx = target.x - self.position.x
        dy = target.y - self.position.y

        # Проверка на диагональное перемещение (|dx| == |dy|)
        if abs(dx) != abs(dy):
            return False

        step = Vector2i(1 if dx > 0 else -1, 1 if dy > 0 else -1)
        current = self.position + step

        while current != target:
            if any(piece.position == current for piece in pieces):
                return False  # Препятствие на пути
            current += step

        # Проверка конечной клетки: либо пуста, либо с вражеской фигурой
        for piece in pieces:
            if piece.position == target:
                return piece.color != self.color  # Разрешено, если чужая

        return True  # Свободна
    
    def is_dark_square(self)->bool:
        return (self.position.x+self.position.y)%2!=0