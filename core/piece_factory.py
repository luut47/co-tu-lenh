from .piece import Piece, PieceType, Color

def create_piece(p_id, p_type, color, x, y):
    return Piece(p_id, p_type, color, (x, y))

def setup_default_pieces():
    """
    Sets up the default 19 pieces per side according to Cờ Tư Lệnh standard.
    RED is at the bottom (Y = 0 to 4).
    BLUE is at the top (Y = 7 to 11).
    Sea is on the left (X = 0 to 2).
    """
    pieces = []
    pid = 1
    
    def add_p(p_type, color, x, y):
        nonlocal pid
        pieces.append(create_piece(pid, p_type, color, x, y))
        pid += 1

    # RED (Bottom)
    add_p(PieceType.COMMANDER, Color.RED, 6, 0)
    add_p(PieceType.NAVY, Color.RED, 1, 1)
    add_p(PieceType.NAVY, Color.RED, 2, 3)
    add_p(PieceType.AIRFORCE, Color.RED, 4, 1)
    add_p(PieceType.AIRFORCE, Color.RED, 8, 1)
    add_p(PieceType.HEADQUARTERS, Color.RED, 5, 1)
    add_p(PieceType.HEADQUARTERS, Color.RED, 7, 1)
    add_p(PieceType.ARTILLERY, Color.RED, 3, 2)
    add_p(PieceType.ARTILLERY, Color.RED, 9, 2)
    add_p(PieceType.MISSILE, Color.RED, 6, 2)
    add_p(PieceType.ANTIAIR, Color.RED, 4, 3)
    add_p(PieceType.ANTIAIR, Color.RED, 8, 3)
    add_p(PieceType.TANK, Color.RED, 5, 3)
    add_p(PieceType.TANK, Color.RED, 7, 3)
    add_p(PieceType.INFANTRY, Color.RED, 2, 4)
    add_p(PieceType.INFANTRY, Color.RED, 10, 4)
    add_p(PieceType.ENGINEER, Color.RED, 3, 4)
    add_p(PieceType.ENGINEER, Color.RED, 9, 4)
    add_p(PieceType.MILITIA, Color.RED, 6, 4)

    # BLUE (Top)
    add_p(PieceType.COMMANDER, Color.BLUE, 6, 11)
    add_p(PieceType.NAVY, Color.BLUE, 1, 10)
    add_p(PieceType.NAVY, Color.BLUE, 2, 8)
    add_p(PieceType.AIRFORCE, Color.BLUE, 4, 10)
    add_p(PieceType.AIRFORCE, Color.BLUE, 8, 10)
    add_p(PieceType.HEADQUARTERS, Color.BLUE, 5, 10)
    add_p(PieceType.HEADQUARTERS, Color.BLUE, 7, 10)
    add_p(PieceType.ARTILLERY, Color.BLUE, 3, 9)
    add_p(PieceType.ARTILLERY, Color.BLUE, 9, 9)
    add_p(PieceType.MISSILE, Color.BLUE, 6, 9)
    add_p(PieceType.ANTIAIR, Color.BLUE, 4, 8)
    add_p(PieceType.ANTIAIR, Color.BLUE, 8, 8)
    add_p(PieceType.TANK, Color.BLUE, 5, 8)
    add_p(PieceType.TANK, Color.BLUE, 7, 8)
    add_p(PieceType.INFANTRY, Color.BLUE, 2, 7)
    add_p(PieceType.INFANTRY, Color.BLUE, 10, 7)
    add_p(PieceType.ENGINEER, Color.BLUE, 3, 7)
    add_p(PieceType.ENGINEER, Color.BLUE, 9, 7)
    add_p(PieceType.MILITIA, Color.BLUE, 6, 7)
    
    return pieces
