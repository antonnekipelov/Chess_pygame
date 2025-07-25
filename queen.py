from typing import List
from colors import Color
from piece import Piece
from vector import Vector2i  # Assuming you have this class

class Queen(Piece):
    def __init__(self, parent_node, pos: Vector2i, clr: str):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}Q.png"
        super().__init__(parent_node, pos, clr, texture_path)
    
    def is_valid_move(self, target: Vector2i, pieces: List[Piece], ignore_checks=False) -> bool:
        # First check basic move validation (can't capture own pieces)
        if not super().is_valid_move(target, pieces, ignore_checks):
            return False

        dx = target.x - self.position.x
        dy = target.y - self.position.y
        
        # Queen can move horizontally, vertically, or diagonally
        is_horizontal = (dy == 0 and dx != 0)
        is_vertical = (dx == 0 and dy != 0)
        is_diagonal = (abs(dx) == abs(dy) and dx != 0)
        
        if not (is_horizontal or is_vertical or is_diagonal):
            return False  # Not a valid queen move

        step = Vector2i(
            sign(dx) if dx != 0 else 0,
            sign(dy) if dy != 0 else 0
        )
        
        current = self.position + step

        # Check path to target
        while current != target:
            for piece in pieces:
                if piece.position == current:
                    return False  # Path is blocked
            current += step

        # Check target square - must be empty or contain enemy
        for piece in pieces:
            if piece.position == target:
                return piece.color != self.color  # Can capture enemy

        return True  # Target square is empty

def sign(x: int) -> int:
    """Helper function to get sign of a number (-1, 0, or 1)"""
    return (x > 0) - (x < 0)