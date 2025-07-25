from colors import Color
from piece import Piece
from vector import Vector2i  # Assuming you have this class

class Knight(Piece):
    def __init__(self, parent_node, pos: Vector2i, clr: str):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}N.png"
        super().__init__(parent_node, pos, clr, texture_path)
    
    def is_valid_move(self, target: Vector2i, pieces: list, ignore_checks=False) -> bool:
        # First check basic move validation (can't capture own pieces)
        if not super().is_valid_move(target, pieces, ignore_checks):
            return False

        dx = abs(target.x - self.position.x)
        dy = abs(target.y - self.position.y)
        
        # Knight moves in L-shape: 2 squares in one direction and 1 square perpendicular
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)