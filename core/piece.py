from enum import Enum


class PieceType(Enum):
    COMMANDER = "Commander"
    INFANTRY = "Infantry"
    TANK = "Tank"
    MILITIA = "Militia"
    ENGINEER = "Engineer"
    ARTILLERY = "Artillery"
    ANTIAIR = "AntiAir"
    MISSILE = "Missile"
    AIRFORCE = "AirForce"
    NAVY = "Navy"
    HEADQUARTERS = "Headquarters"


class Color(Enum):
    RED = "RED"
    BLUE = "BLUE"


class Piece:
    def __init__(self, piece_id, piece_type, color, position, is_hero=False):
        self.id = piece_id
        self.type = piece_type
        self.color = color
        self.position = position
        self.is_hero = is_hero
        self.stacked_pieces = []

    def move_to(self, new_position):
        self.position = new_position
        for p in self.stacked_pieces:
            p.move_to(new_position)

    def add_to_stack(self, piece):
        piece.move_to(self.position)
        self.stacked_pieces.append(piece)

    def get_all_types_in_stack(self):
        types = [self.type]
        for p in self.stacked_pieces:
            types.append(p.type)
        return types
