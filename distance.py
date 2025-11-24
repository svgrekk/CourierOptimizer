import math

R = 6371.0


def haver_dist(lati1, long1, lati2, long2):
    lati1 = math.radians(lati1)
    long1 = math.radians(long1)
    lati2 = math.radians(lati2)
    long2 = math.radians(long2)
    dlong = long2 - long1
    dlati = lati2 - lati1
    a = (
            math.sin(dlati / 2) ** 2
            + math.cos(lati1) * math.cos(lati2) * math.sin(dlong / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance
