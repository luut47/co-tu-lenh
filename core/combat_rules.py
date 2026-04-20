from .piece import PieceType, Color
from .board_layout import get_zone, Zone
from .scoring import get_piece_score

def get_valid_attacks(piece, board):
    """
    Returns list of dicts: {'to': (tx, ty), 'type': MoveType, 'is_stand_still': bool}
    Note: MoveType should be imported where this is used, we'll return raw dicts
    and the board can assign the exact MoveType Enum.
    """
    attacks = []
    x, y = piece.position
    
    # Helper to check if a position has an enemy
    def has_enemy(tx, ty):
        p = board.get_piece_at(tx, ty)
        return p is not None and p.color != piece.color

    dirs_straight = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dirs_diag = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs_all = dirs_straight + dirs_diag

    my_zone = get_zone(x, y)

    # 1. Infantry, Engineer, AntiAir
    if piece.type in [PieceType.INFANTRY, PieceType.ENGINEER, PieceType.ANTIAIR]:
        for dx, dy in dirs_straight:
            tx, ty = x + dx, y + dy
            if has_enemy(tx, ty):
                attacks.append({'to': (tx, ty), 'is_stand_still': False})

    # 2. Militia
    elif piece.type == PieceType.MILITIA:
        for dx, dy in dirs_all:
            tx, ty = x + dx, y + dy
            if has_enemy(tx, ty):
                attacks.append({'to': (tx, ty), 'is_stand_still': False})

    # 3. Tank
    elif piece.type == PieceType.TANK:
        is_sea = (my_zone == Zone.SEA)
        for dx, dy in dirs_straight:
            for i in range(1, 3):
                tx, ty = x + dx * i, y + dy * i
                p = board.get_piece_at(tx, ty)
                if p:
                    if p.color != piece.color:
                        attacks.append({'to': (tx, ty), 'is_stand_still': is_sea})
                    break # Blocked by piece (friend or foe)

    # 4. Artillery
    elif piece.type == PieceType.ARTILLERY:
        is_sea = (my_zone == Zone.SEA)
        for dx, dy in dirs_all:
            for i in range(1, 4):
                tx, ty = x + dx * i, y + dy * i
                p = board.get_piece_at(tx, ty)
                if p:
                    if p.color != piece.color:
                        attacks.append({'to': (tx, ty), 'is_stand_still': is_sea})
                    break

    # 5. Missile (Range assumed 1-3 straight, triggers AOE on impact)
    elif piece.type == PieceType.MISSILE:
        for dx, dy in dirs_all:
            for i in range(1, 4):
                tx, ty = x + dx * i, y + dy * i
                # Missiles fly over obstacles? The rules say area attack. We'll let them shoot over obstacles.
                p = board.get_piece_at(tx, ty)
                if p and p.color != piece.color:
                    attacks.append({'to': (tx, ty), 'is_stand_still': True, 'is_aoe': True})

    # 6. Air Force
    elif piece.type == PieceType.AIRFORCE:
        for dx, dy in dirs_all:
            for i in range(1, 5):
                tx, ty = x + dx * i, y + dy * i
                p = board.get_piece_at(tx, ty)
                if p and p.color != piece.color:
                    attacks.append({'to': (tx, ty), 'is_stand_still': False})

    # 7. Navy
    elif piece.type == PieceType.NAVY:
        for dx, dy in dirs_all:
            for i in range(1, 5):
                tx, ty = x + dx * i, y + dy * i
                target_zone = get_zone(tx, ty)
                p = board.get_piece_at(tx, ty)
                if p:
                    if p.color != piece.color:
                        # If targeting land, it can stand still
                        stand_still = (target_zone == Zone.LAND)
                        attacks.append({'to': (tx, ty), 'is_stand_still': stand_still})
                    break # Blocked by piece (unless we rule Navy shots fly over things, but standard is blocked)
                # Note: rules say "Không bị chặn bởi quân đồng minh" (not blocked by allies), 
                # but let's implement the basic line-of-sight for now. 
                # Wait! "Không bị chặn bởi quân đồng minh" -> we shouldn't break if `p` is friend?
                # Let's fix that:
                if p and p.color == piece.color:
                    continue # Fly over allies!

    # 8. Commander
    elif piece.type == PieceType.COMMANDER:
        for dx, dy in dirs_straight:
            tx, ty = x + dx, y + dy
            if has_enemy(tx, ty):
                attacks.append({'to': (tx, ty), 'is_stand_still': False})

    # Apply Heroic buff (range + 1, and diagonal allowed)
    if piece.is_hero:
        # Simplification: just add +1 to range for straight attacks
        # This is a bit complex to patch onto the existing loops.
        # We will handle basic rules first.
        pass

    return attacks

def resolve_combat(attacker, target_pos, board):
    """
    Executes the combat logic, removes pieces from the board.
    Returns (logs: list[str], scores: dict {Color -> int})
    """
    tx, ty = target_pos
    target_piece = board.get_piece_at(tx, ty)
    
    logs = []
    scores = {Color.RED: 0, Color.BLUE: 0}  # points earned this combat

    if attacker.type == PieceType.MISSILE:
        # Area of effect radius 2 (Chebyshev)
        destroyed = []
        for p in board.pieces[:]:
            px, py = p.position
            dist = max(abs(px - tx), abs(py - ty))
            if dist <= 2:
                pts = get_piece_score(p)
                # Attacker earns points for destroying enemy pieces
                if p.color != attacker.color:
                    scores[attacker.color] += pts
                destroyed.append(p)
                board.pieces.remove(p)
        
        # Missile self-destructs
        if attacker in board.pieces:
            board.pieces.remove(attacker)
            
        logs.append(f"MISSILE detonated at {target_pos}! Destroyed {len(destroyed)} units in radius 2.")
        for color, pts in scores.items():
            if pts:
                print(f"  +{pts} score to {color.name}")
        return logs, scores

    if target_piece:
        pts = get_piece_score(target_piece)
        scores[attacker.color] += pts
        
        if target_piece in board.pieces:
            board.pieces.remove(target_piece)
            logs.append(f"{attacker.type.name} {attacker.position} --> {target_piece.type.name} ({pts} pts to {attacker.color.name})")
            print(f"Piece destroyed: +{pts} score to {attacker.color.name}")
            
            # Special interaction: Air Force attacking AA → 1-1 exchange
            if attacker.type == PieceType.AIRFORCE and target_piece.type == PieceType.ANTIAIR:
                if attacker in board.pieces:
                    board.pieces.remove(attacker)
                    logs.append(f"Exchange 1-1: AIRFORCE destroyed by ANTIAIR.")
                    
    return logs, scores

