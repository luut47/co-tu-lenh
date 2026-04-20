from enum import Enum

class Zone(Enum):
    LAND = "LAND"
    SEA = "SEA"
    RIVER = "RIVER"
    FORD = "FORD"

# Board dimensions
COLS = 11
ROWS = 12

# Zones definitions
# River spans horizontally at row 5
RIVER_ROWS = [5]

# Fords are specific X coordinates crossing the river
FORD_COLS = [4, 6]

# Sea covers specific columns on the left (0, 1)
SEA_COLS_LEFT = [0, 1]

def get_zone(x, y):
    """
    Returns the Zone for a given (x, y) intersection.
    """
    if x < 0 or x >= COLS or y < 0 or y >= ROWS:
        return None # Out of bounds
        
    # Check Sea
    if x in SEA_COLS_LEFT:
        return Zone.SEA
        
    # Check River & Ford
    if y in RIVER_ROWS:
        # Ford is only defined on the river rows
        if x in FORD_COLS:
            return Zone.FORD
        # If it's not a ford, it's river
        return Zone.RIVER
        
    # Default is land
    return Zone.LAND
