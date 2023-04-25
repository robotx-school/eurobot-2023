from math import degrees, atan2

# Vector math
def vect_from_4points(x, y, x1, y1):
    """Returns the vector between 2 points (x, y) and (x1, y1)."""
    return x1 - x, y1 - y

def angle_between_2vectors(ax, ay, bx, by):
    """Returns the angle between two given vectors in degrees."""
    return degrees(atan2(ax * by - ay * bx, ax * bx + ay * by))
