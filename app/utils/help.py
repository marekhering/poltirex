import math


def dist_calc(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    return math.sqrt((a_lat - b_lat) ** 2 + (a_lon - b_lon) ** 2)
