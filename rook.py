from typing import List
from colors import Color
from piece import Piece
from vector import Vector2i

class Rook(Piece):
    def __init__(self, parent_node, pos, clr: str):
        color_prefix = "b" if clr == Color.BLACK else "w"
        texture_path = f"assets/{color_prefix}R.png"
        super().__init__(parent_node, pos, clr, texture_path)
    
    def is_valid_move(self, target: Vector2i, pieces: List[Piece], ignore_checks=False) -> bool:
        # First check basic move validation (can't capture own pieces)
        if not super().is_valid_move(target, pieces, ignore_checks):
            return False

        # Rook must move in straight line (same row or column)
        if self.position.x != target.x and self.position.y != target.y:
            return False

        # Determine direction of movement
        step = Vector2i(
            sign(target.x - self.position.x),
            sign(target.y - self.position.y)
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