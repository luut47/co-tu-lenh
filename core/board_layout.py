from enum import Enum


class Zone(Enum):
    LAND = "LAND"
    SEA = "SEA"
    RIVER = "RIVER"
    FORD = "FORD"


COLS = 11
ROWS = 12

RIVER_ROWS = [5]
SEA_COLS = [0, 1]
FORD_COLS = [5, 7]
RIVER_MOUTH_DEPTH = 3


def in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS


def is_sea(x, y):
    return in_bounds(x, y) and x in SEA_COLS


def is_river(x, y):
    return in_bounds(x, y) and y in RIVER_ROWS and x not in SEA_COLS


def is_ford(x, y):
    return in_bounds(x, y) and x in FORD_COLS and y in RIVER_ROWS and x not in SEA_COLS


def is_coast_border(x, y):
    if not in_bounds(x, y):
        return False
    if get_zone(x, y) != Zone.LAND:
        return False
    return any(in_bounds(nx, ny) and get_zone(nx, ny) == Zone.SEA for nx, ny in (
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ))


def is_river_mouth(x, y):
    if not in_bounds(x, y) or y not in RIVER_ROWS:
        return False
    river_edge_x = max(SEA_COLS) + 1
    return river_edge_x - (RIVER_MOUTH_DEPTH - 1) <= x <= river_edge_x


def get_zone(x, y):
    if not in_bounds(x, y):
        return None
    if is_ford(x, y):
        return Zone.FORD
    if is_sea(x, y):
        return Zone.SEA
    if is_river(x, y):
        return Zone.RIVER
    return Zone.LAND
