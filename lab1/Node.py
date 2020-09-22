_authors = "kvp"

"""
Author 1: Venkata Karteek Paladugu (vp3982@rit.edu)


"""


class Node:
    """
    A node to represent node in graph
    """
    __slots__ = 'x', 'y', 'z', 'connected_to', 'terrain'

    def __init__(self, x, y, z=None, terrain=None):
        self.x = x
        self.y = y
        self.z = z
        self.terrain = terrain
        self.connected_to = dict()

    def getSpeed(self):
        return self.speed_dict[self.terrain]

    def add_neighbor(self, nbr, cost):
        self.connected_to[nbr] = cost

    def get_connections(self):
        return self.connected_to.keys()

    def __lt__(self, other):
        return self.x == other.x and self.y < other.y
