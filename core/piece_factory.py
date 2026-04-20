from .piece import Piece, PieceType, Color

def create_piece(p_id, p_type, color, x, y):
    return Piece(p_id, p_type, color, (x, y))

def setup_default_pieces():
    """
    Sets up the default 31-32 pieces per side.
    This is an approximation based on standard Cờ Tư Lệnh layout.
    RED is at the bottom (Y = 0 to 4).
    BLUE is at the top (Y = 7 to 11).
    """
    pieces = []
    pid = 1
    
    # helper to add a piece and auto-increment ID
    def add_p(p_type, color, x, y):
        nonlocal pid
        pieces.append(create_piece(pid, p_type, color, x, y))
        pid += 1

    # RED (Bottom)
    add_p(PieceType.COMMANDER, Color.RED, 5, 0)
    add_p(PieceType.AIRFORCE, Color.RED, 4, 1)
    add_p(PieceType.AIRFORCE, Color.RED, 6, 1)
    add_p(PieceType.HEADQUARTERS, Color.RED, 5, 2)
    add_p(PieceType.ARTILLERY, Color.RED, 3, 2)
    add_p(PieceType.ARTILLERY, Color.RED, 7, 2)
    add_p(PieceType.MISSILE, Color.RED, 5, 1)
    add_p(PieceType.NAVY, Color.RED, 1, 1)
    add_p(PieceType.NAVY, Color.RED, 1, 3)
    add_p(PieceType.ANTIAIR, Color.RED, 2, 3)
    add_p(PieceType.ANTIAIR, Color.RED, 8, 3)
    add_p(PieceType.TANK, Color.RED, 4, 3)
    add_p(PieceType.TANK, Color.RED, 6, 3)
    add_p(PieceType.ENGINEER, Color.RED, 2, 4)
    add_p(PieceType.ENGINEER, Color.RED, 8, 4)
    add_p(PieceType.INFANTRY, Color.RED, 3, 4)
    add_p(PieceType.INFANTRY, Color.RED, 5, 4)
    add_p(PieceType.INFANTRY, Color.RED, 7, 4)
    add_p(PieceType.MILITIA, Color.RED, 6, 4)

    # BLUE (Top)
    add_p(PieceType.COMMANDER, Color.BLUE, 5, 11)
    add_p(PieceType.AIRFORCE, Color.BLUE, 4, 10)
    add_p(PieceType.AIRFORCE, Color.BLUE, 6, 10)
    add_p(PieceType.HEADQUARTERS, Color.BLUE, 5, 9)
    add_p(PieceType.ARTILLERY, Color.BLUE, 3, 9)
    add_p(PieceType.ARTILLERY, Color.BLUE, 7, 9)
    add_p(PieceType.MISSILE, Color.BLUE, 5, 10)
    add_p(PieceType.NAVY, Color.BLUE, 1, 10)
    add_p(PieceType.NAVY, Color.BLUE, 1, 8)
    add_p(PieceType.ANTIAIR, Color.BLUE, 2, 8)
    add_p(PieceType.ANTIAIR, Color.BLUE, 8, 8)
    add_p(PieceType.TANK, Color.BLUE, 4, 8)
    add_p(PieceType.TANK, Color.BLUE, 6, 8)
    add_p(PieceType.ENGINEER, Color.BLUE, 2, 7)
    add_p(PieceType.ENGINEER, Color.BLUE, 8, 7)
    add_p(PieceType.INFANTRY, Color.BLUE, 3, 7)
    add_p(PieceType.INFANTRY, Color.BLUE, 5, 7)
    add_p(PieceType.INFANTRY, Color.BLUE, 7, 7)
    add_p(PieceType.MILITIA, Color.BLUE, 6, 7)
    
    return pieces
