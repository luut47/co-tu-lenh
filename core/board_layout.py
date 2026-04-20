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
# River spans horizontally between row 5 and 6
RIVER_ROWS = [5, 6]

# Fords are specific X coordinates crossing the river
FORD_COLS = [4, 6]

# Sea covers specific columns (e.g. left side)
# We can adjust this to match the exact rules or images
SEA_COLS_LEFT = [0, 1]
SEA_COLS_RIGHT = [9, 10]

def get_zone(x, y):
    """
    Returns the Zone for a given (x, y) intersection.
    """
    if x < 0 or x >= COLS or y < 0 or y >= ROWS:
        return None # Out of bounds
        
    # Check Sea
    if x in SEA_COLS_LEFT or x in SEA_COLS_RIGHT:
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
