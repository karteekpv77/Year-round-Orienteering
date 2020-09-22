import re
import sys
from math import sqrt
from queue import PriorityQueue

from PIL import Image

from graph import Graph

_authors = "kvp"

"""
Author 1: Venkata Karteek Paladugu (vp3982@rit.edu)
This is a code to find shortest path from one point to other 

"""


def read_image(pixels, width, length):
    """

    :param pixels: all the pixels of the image
    :param width: width of pixel
    :param length: length of pixel
    :return: pixel array
    """
    all_pixels = [[(0, 0, 0) for x in range(length)] for x in range(width)]
    for x in range(width):
        for y in range(length):
            cpixel = pixels[x, y][0:3]
            all_pixels[x][y] = cpixel
    return all_pixels


def get_heuristic(src, dest, graph):
    """

    :param src: start point
    :param dest: goal point
    :param graph: graph of all nodes
    :return: heuristic distance from start to goal
    """
    distance = sqrt((((dest.x - src.x) * 10.29) ** 2) + (((dest.y - src.y) * 7.55) ** 2) + ((dest.z - src.z) ** 2))
    return distance / graph.get_speed_dict()[(71, 51, 3)]


def form_ice_or_mud(waterlist, graph, season):
    """

    :param waterlist: all pixels which are borders of water and land
    :param graph: grph of all nodes
    :param season: season type
    :return: returns all nodes that are eligible to change in that season
    """
    max_depth = 0
    if season is 'winter':
        max_depth = 8
    elif season is 'spring':
        max_depth = 15
    nodes = []
    for water in waterlist:
        node = graph.getNode((water[0], water[1]))
        if node.terrain == (0, 0, 255):
            nodes.append(bfs(node, graph, season, max_depth))
    return nodes


def bfs(main_node, graph, season, max_depth):
    """

    :param main_node: start node
    :param graph: grph of all nodes
    :param season: season type
    :param max_depth: depth to explore
    :return: all nodes visited upto the given depth
    """
    is_winter = False
    is_spring = False
    visited = set()
    if season is 'winter':
        changed_terrain = (63, 208, 212)
        main_node.terrain = (63, 208, 212)
        is_winter = True
        visited.add((main_node.x, main_node.y))
    elif season is 'spring':
        changed_terrain = (139, 69, 19)
        elevation = main_node.z
        is_spring = True

    depth = 1

    frontier = [main_node]

    while depth < max_depth and len(frontier) > 0:
        node = frontier.pop(0)
        for connected_node in node.get_connections():
            if (connected_node.x, connected_node.y) not in visited and (
                    (is_winter and connected_node.terrain == (0, 0, 255)) or (
                    is_spring and connected_node.terrain != (0, 0, 255) and (connected_node.z - elevation < 1))):
                frontier.append(connected_node)
                visited.add((connected_node.x, connected_node.y))
                connected_node.terrain = changed_terrain
                node.add_neighbor(connected_node,
                                  graph.get_cost(node.x, node.y, node.z, connected_node.x, connected_node.y,
                                                 connected_node.z))

        depth += 1
    return list(visited)


def search(src, dest, graph, elevations):
    """

    :param src: start point of the path
    :param dest: goal point
    :param graph: graph of all nodes
    :param elevations: all the elevations of different pixels
    :return:
    """
    remaining = PriorityQueue()
    remaining.put((0 + get_heuristic(src, dest, graph), (src, None)))
    visited = set()
    came_from = {}
    total_cost = {}
    while not remaining.empty():
        min_node_cost_tuple = remaining.get()
        min_node_tuple = min_node_cost_tuple[1]
        min_node = min_node_tuple[0]
        came_from[(min_node.x, min_node.y)] = min_node_tuple[1]
        cost = min_node_cost_tuple[0] - get_heuristic(min_node, dest, graph)
        total_cost[min_node] = cost
        if (min_node.x, min_node.y) in visited:
            continue
        if min_node.x == dest.x and min_node.y == dest.y:
            visited.add((min_node.x, min_node.y))
            return came_from, total_cost
        visited.add((min_node.x, min_node.y))
        for connected_node in min_node.get_connections():
            if (connected_node.x, connected_node.y) not in visited:
                remaining.put((
                    cost + min_node.connected_to[connected_node] + get_heuristic(connected_node, dest, graph),
                    (connected_node, (min_node.x, min_node.y))))
    return came_from, total_cost


def main():
    """
    This is the main function of the path writing program it uses A* search to find shortest path between two points
    :return:
    """
    # terrain png file
    terrain = sys.argv[1]
    # elevtion txt file
    elevation = sys.argv[2]
    # paths txt file
    path = sys.argv[3]
    # season string
    season = sys.argv[4]
    # image file
    output = sys.argv[5]
    points = []
    im = Image.open(terrain)
    pixels = im.load()  # this is not a list, nor is it list()'able
    img = im.copy()
    pixelsNew = img.load()
    width, height = im.size
    all_pixels = read_image(pixels, width, height)
    elevation_width = 395
    elevation_length = 500
    elevations = [[0 for x in range(elevation_length)] for x in range(elevation_width)]
    with open(elevation) as f:
        line_number = 0
        for line in f.readlines():
            column_number = 0
            for number in re.split('[\s]+', line.strip()):
                if column_number < 395:
                    elevations[column_number][line_number] = float(number)
                column_number += 1
            line_number += 1
    graph = Graph(all_pixels, elevations, elevation_width, elevation_length, season)
    ice_points = form_ice_or_mud(graph.waterlist, graph, season)
    if season is 'winter':
        changed_terrain = (63, 208, 212, 255)
    elif season is 'spring':
        changed_terrain = (139, 69, 19, 255)
    for ice_point in ice_points:
        for each_point in ice_point:
            pixelsNew[each_point[0], each_point[1]] = changed_terrain
    with open(path) as f:
        for line in f.readlines():
            points.append(tuple(map(int, line.strip().split(' '))))
    index = 0
    results = []
    total_cost = 0
    total_distance = 0
    # calculating total cost and distance based on the points
    while index + 1 < len(points):
        came_from, cost = search(graph.getNode(points[index]), graph.getNode(points[index + 1]), graph, elevations)
        start = points[index + 1]
        result = []
        result.insert(0, start)
        while came_from[start] is not None:
            src = start
            dest = came_from[start]
            total_cost = total_cost + cost[graph.getNode(dest)]
            distance = graph.get_distance(src[0], src[1], elevations[src[0]][src[1]], dest[0], dest[1],
                                          elevations[dest[0]][dest[1]])
            total_distance = total_distance + distance
            result.insert(0, dest)
            start = dest
        results.append(result)
        index += 1
    print("Total distance is :" + str(total_distance))
    print("Total seconds:" + str(total_cost))
    for point in points:
        x = point[0]
        y = point[1]
        if x - 1 >= 0 and y - 1 >= 0:
            pixelsNew[x - 1, y - 1] = (0, 0, 139, 255)
        if x + 1 < width and y + 1 < height:
            pixelsNew[x + 1, y + 1] = (0, 0, 139, 255)
        if x - 1 >= 0:
            pixelsNew[x - 1, y] = (0, 0, 139, 255)
        if y - 1 >= 0:
            pixelsNew[x, y - 1] = (0, 0, 139, 255)
        if x + 1 < width:
            pixelsNew[x + 1, y] = (0, 0, 139, 255)
        if y + 1 < height:
            pixelsNew[x, y + 1] = (0, 0, 139, 255)
        if x + 1 < width and y - 1 >= 0:
            pixelsNew[x + 1, y - 1] = (0, 0, 139, 255)
        if x - 1 >= 0 and y + 1 < height:
            pixelsNew[x - 1, y + 1] = (0, 0, 139, 255)

    for result in results:
        for each_point in result:
            pixelsNew[each_point[0], each_point[1]] = (255, 0, 0, 255)
    img.save(output)


main()
