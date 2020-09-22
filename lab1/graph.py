_authors = "kvp"

"""
Author 1: Venkata Karteek Paladugu (vp3982@rit.edu)


"""
from math import sqrt, cos, atan

from Node import Node


class Graph:
    """
    A graph implemented as an adjacency list of vertices.

    :slot: vertList (dict):  A dictionary that maps a vertex key to a Vertex
        object
    :slot: numVertices (int):  The total number of vertices in the graph
    :slot speed_dict (dict): dictionary of terrains and their speeds
    :sl
    """

    __slots__ = 'vertList', 'numVertices', 'speed_dict', 'season', 'waterlist'

    def __init__(self, all_pixels, elevations, width, length, season):
        """

        :param all_pixels: all pixels of image
        :param elevations: all elevations of image
        :param width: widht of image
        :param length: length of image
        :param season: season type
        """
        self.vertList = {}
        self.waterlist = []
        self.numVertices = 0
        self.speed_dict = {(248, 148, 18): 1.4,
                           (255, 192, 0): 1.25,
                           (255, 255, 255): 1.33,
                           (2, 208, 60): 1.15,
                           (2, 136, 40): 1.05,
                           (5, 73, 24): 0.15,
                           (0, 0, 255): 0.1,
                           (71, 51, 3): 1.55,
                           (0, 0, 0): 1.45,
                           (205, 0, 101): 0.001,  # out of bounds
                           (63, 208, 212): 0.9,  # ice
                           (139, 69, 19): 0.95  # mud
                           }
        if season.lower() == 'fall':
            self.speed_dict[255, 255, 255] = 1.10

        self.season = season
        is_winter = False
        if self.season.lower() == 'winter' or self.season.lower() == 'spring':
            is_winter = True
        has_land = False
        is_water = False
        for x in range(width):
            for y in range(length):
                if all_pixels[x][y] == (0, 0, 255):
                    is_water = True
                    has_land = False
                if x - 1 >= 0 and y - 1 >= 0:
                    if is_water and is_winter and all_pixels[x - 1][y - 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x - 1, y - 1, elevations, all_pixels)
                if x + 1 < width and y + 1 < length:
                    if is_water and is_winter and all_pixels[x + 1][y + 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x + 1, y + 1, elevations, all_pixels)
                if x - 1 >= 0:
                    if is_water and is_winter and all_pixels[x - 1][y] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x - 1, y, elevations, all_pixels)
                if y - 1 >= 0:
                    if is_water and is_winter and all_pixels[x][y - 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x, y - 1, elevations, all_pixels)
                if x + 1 < width:
                    if is_water and is_winter and all_pixels[x + 1][y] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x + 1, y, elevations, all_pixels)
                if y + 1 < length:
                    if is_water and is_winter and all_pixels[x][y + 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x, y + 1, elevations, all_pixels)
                if x + 1 < width and y - 1 >= 0:
                    if is_water and is_winter and all_pixels[x + 1][y - 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x + 1, y - 1, elevations, all_pixels)
                if x - 1 >= 0 and y + 1 < length:
                    if is_water and is_winter and all_pixels[x - 1][y + 1] != (0, 0, 255):
                        has_land = True
                    self.addEdge(x, y, x - 1, y + 1, elevations, all_pixels)
                if has_land and is_winter and is_water:
                    self.waterlist.append((x, y))
                    is_water = False

    def get_waterlist(self):
        return self.waterlist

    def get_speed_dict(self):
        return self.speed_dict

    def addNode(self, node):
        """
        Add a new vertex to the graph.
        :param node: node to be added
        :return: Vertex
        """
        # count this vertex if not already present
        if self.getNode((node.x, node.y)) is None:
            self.numVertices += 1
            self.vertList[(node.x, node.y)] = node
        return node

    def getNode(self, key):
        """
        Retrieve the vertex from the graph.
        :param key: The vertex identifier
        :return: Vertex if it is present, otherwise None
        """
        if key in self.vertList:
            return self.vertList[key]
        else:
            return None

    def __contains__(self, key):
        """
        Returns whether the vertex is in the graph or not.  This allows the
        user to do:

            key in graph

        :param key: The vertex identifier
        :return: True if the vertex is present, and False if not
        """
        return key in self.vertList

    def addEdge(self, src_x, src_y, dest_x, dest_y, elevations, pixels):
        """
        Add a new directed edge from a source to a destination of an edge cost.
        :param pixels: all pixels in image
        :param src_x: source x coordinate
        :param src_y: source y coordinate
        :param elevations: all elevations of image
        :param dest_y: destination  x coordinate
        :param dest_x:destination y coordinate
        :return: None
        """
        src_z = elevations[src_x][src_y]
        dest_z = elevations[dest_x][dest_y]
        if (src_x, src_y, src_z) not in self.vertList:
            self.addNode(Node(src_x, src_y, src_z, pixels[src_x][src_y]))
        if (dest_x, dest_y, dest_z) not in self.vertList:
            self.addNode(Node(dest_x, dest_y, dest_z, pixels[dest_x][dest_y]))
            cost = self.get_cost(src_x, src_y, src_z, dest_x, dest_y, dest_z)
            self.vertList[(src_x, src_y)].add_neighbor(self.vertList[(dest_x, dest_y)], cost)

    def get_cost(self, src_x, src_y, src_z, dest_x, dest_y, dest_z):
        """
        Add a new directed edge from a source to a destination of an edge cost.
        :param src_x: source x coordinate
        :param src_y: source y coordinate
        :param src_z: source elevation
        :param dest_y: destination  x coordinate
        :param dest_x:destination y coordinate
        :param dest_z: destination elevation
        :return: None
        """
        distance = sqrt((((dest_x - src_x) * 10.29) ** 2) + (((dest_y - src_y) * 7.55) ** 2))
        angle = (dest_z - src_z) / distance
        multiplier = 1
        if angle != 0:
            multiplier = cos(atan(angle))
        if angle < 0:
            multiplier = 2 * multiplier
        cost = distance / (self.speed_dict[self.vertList[(dest_x, dest_y)].terrain] * multiplier)
        return cost

    def get_distance(self, src_x, src_y, src_z, dest_x, dest_y, dest_z):
        """
        Add a new directed edge from a source to a destination of an edge cost.
        :param src_x: source x coordinate
        :param src_y: source y coordinate
        :param src_z: source elevation
        :param dest_y: destination  x coordinate
        :param dest_x:destination y coordinate
        :param dest_z: destination elevation
        :return: distance
        """

        distance = sqrt((((dest_x - src_x) * 10.29) ** 2) + (((dest_y - src_y) * 7.55) ** 2) + ((dest_z - src_z) ** 2))
        return distance

    def __iter__(self):
        """
            Return an iterator over the vertices in the graph.  This allows the
            user to do:

                for vertex in graph:
                    ...

            :return: A list iterator over Vertex objects
            """
        return iter(self.vertList.values())
