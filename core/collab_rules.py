from .piece import PieceType

def can_combine(piece_a, piece_b):
    """
    Check if two pieces can be combined into a stack.
    Example: Infantry can ride on a Tank.
    """
    if piece_a.color != piece_b.color:
        return False
        
    types = {piece_a.type, piece_b.type}
    if types == {PieceType.INFANTRY, PieceType.TANK}:
        return True
    if types == {PieceType.MILITIA, PieceType.TANK}:
        return True
        
    return False

def check_air_defense(board, path):
    """
    Check if an air path crosses an active anti-air zone.
    """
    # Stub implementation
    return False
