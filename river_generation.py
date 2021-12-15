from itertools import groupby
from typing import List, Dict, Set
import heapq
import random

from shapely import geometry, validation
import matplotlib.pyplot as plt

import foronoi
import numpy as np
from foronoi import Voronoi, Polygon, Visualizer, Point, VoronoiObserver
from foronoi.visualization.visualizer import Colors
from foronoi.graph import HalfEdge, Vertex


def path_vertex(vertex: Vertex):
    def __gt__(self, other):
        return self.xy > other.xy

    def __lt__(self, other):
        return self.xy < other.xy

    def __eq__(self, other):
        return self.xy == other.xy

    vertex.__gt__ = __gt__
    vertex.__eq__ = __eq__
    vertex.__lt__ = __lt__


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item, priority: float):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Graph:

    def __init__(self, edges: Dict[Vertex, List[Vertex]]):
        self.vertex_edges = edges
        self.edges = {k.xy: [i.xy for i in v] for k, v in self.vertex_edges.items()}
        self.weights = {k: {i: self._distance(k, i) for i in v} for k, v in self.edges.items()}

    def neighbours(self, location):
        return self.edges[location]

    def cost(self, from_node, to_node):
        return self.weights[from_node].get(to_node, float('inf'))

    @staticmethod
    def _distance(a, b):
        x1, y1 = a
        x2, y2 = b
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5


class RiverGeneration:

    def __init__(self, length, points_num):
        # np.random.seed(2)
        self.points = np.random.randint(0, length, (points_num, 2))
        x_min, y_min, x_max, y_max = (self.points[:, 0].min(), self.points[:, 1].min(),
                                      self.points[:, 0].max(), self.points[:, 1].max())
        self.bounding_poly = [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)]
        self.bounding_poly = Polygon(self.bounding_poly)
        self.voronoi = foronoi.Voronoi(self.bounding_poly)
        self.voronoi.create_diagram(self.points)  # TODO: Lloyd iteration
        self.graph = self.get_graph()

    def get_graph(self):
        graph = {}
        for edge in self.voronoi.edges:
            edge = edge
            origin, target = edge.origin, edge.target
            if origin in graph:
                graph[origin].append(target)
            else:
                graph[origin] = [target]
            edge = edge.twin
            origin, target = edge.origin, edge.target
            if origin in graph:
                graph[origin].append(target)
            else:
                graph[origin] = [target]
        return Graph(graph)

    @staticmethod
    def line_eq_from_points(p1, p2):
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = a * p1[0] + b * p1[1]
        return a, b, c

    @staticmethod
    def is_point_on_line(p, a, b, c):
        # TODO: поченить точность с помощью Decimal
        precision = 13
        x, y = round(p[0], precision), round(p[1], precision)
        return a * x + b * y == c

    def get_points_on_lines(self, points: Set[Vertex], line_eqs_coefficients):
        points_on_lines = set()
        for i in points:
            if any(self.is_point_on_line(i.xy, a, b, c) for a, b, c in line_eqs_coefficients):
                points_on_lines.add(i)

        return points_on_lines

    def get_start_edges_from_points(self, points: Set[Vertex]):
        """Находим ребря не лежащие на ограничивающем полигоне"""
        extended_vertices = {j for i in points for j in i.connected_edges}
        start_edges = set()
        poly_points = self.bounding_poly.points + [self.bounding_poly.points[0]]
        polygon_lines = [(poly_points[i - 1], poly_points[i])
                         for i in range(1, len(poly_points))]
        polygon_lines_eqs_coefficients = [self.line_eq_from_points(p1.xy, p2.xy)
                                          for p1, p2 in polygon_lines]
        for vrx in extended_vertices:
            if (not any(self.is_point_on_line(vrx.target.xy, a, b, c)
                        for a, b, c in polygon_lines_eqs_coefficients)
                    or not any(self.is_point_on_line(vrx.origin.xy, a, b, c)
                               for a, b, c in polygon_lines_eqs_coefficients)):
                start_edges.add(vrx)

        return start_edges

    def get_start_edges(self):
        """Находим ребра которые выходят снизу диаграммы Вороного"""
        lowest_poly_vertices = list(
            next(groupby(sorted(self.bounding_poly.points, key=lambda p: p.y),
                         key=lambda x: x.y))[1])
        poly_points = lowest_poly_vertices + [lowest_poly_vertices[0]]
        polygon_lines = [(poly_points[i - 1], poly_points[i])
                         for i in range(1, len(poly_points))]
        polygon_lines_eqs_coefficients = [self.line_eq_from_points(p1.xy, p2.xy)
                                          for p1, p2 in polygon_lines]
        voronoi_vertices_points = {j for i in self.voronoi.edges for j in (i.origin, i.twin.origin)}

        lowest_voronoi_vertices = self.get_points_on_lines(voronoi_vertices_points,
                                                           polygon_lines_eqs_coefficients)
        start_edges = self.get_start_edges_from_points(lowest_voronoi_vertices)

        return start_edges

    def get_end_points(self):
        highest_poly_vertices = list(
            next(groupby(sorted(self.bounding_poly.points, key=lambda p: p.y, reverse=True),
                         key=lambda x: x.y))[1])
        poly_points = highest_poly_vertices + [highest_poly_vertices[0]]
        polygon_lines = [(poly_points[i - 1], poly_points[i])
                         for i in range(1, len(poly_points))]
        polygon_lines_eqs_coefficients = [self.line_eq_from_points(p1.xy, p2.xy)
                                          for p1, p2 in polygon_lines]
        voronoi_vertices_points = {j for i in self.voronoi.edges for j in (i.origin, i.twin.origin)}
        highest_voronoi_vertices = self.get_points_on_lines(voronoi_vertices_points,
                                                            polygon_lines_eqs_coefficients)
        highest_voronoi_vertices = {vert for vert in highest_voronoi_vertices
                                    if not any(vert.xy == i.xy for i in self.bounding_poly.points)}
        return highest_voronoi_vertices

    def a_star_search(self, start, destination):
        start = start
        destination = destination
        frontier = PriorityQueue()
        frontier.put(start, False)
        came_from = dict()
        cost_so_far = dict()
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == destination:
                break

            for neighbour_edge in self.graph.neighbours(current):
                nxt = neighbour_edge
                new_cost = cost_so_far[current] + self.graph.cost(current, nxt)
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    heuristic = self.heuristic(destination, nxt)
                    if nxt == destination:
                        heuristic = 0
                    if heuristic is None:
                        continue
                    priority = new_cost + heuristic
                    frontier.put(nxt, priority)
                    came_from[nxt] = current

        return came_from, cost_so_far

    def heuristic(self, p1, p2):
        # x1, y1 = p1
        # x2, y2 = p2
        poly_points = self.bounding_poly.points + [self.bounding_poly.points[0]]
        polygon_lines = [(poly_points[i - 1], poly_points[i])
                         for i in range(1, len(poly_points))]
        polygon_lines_eqs_coefficients = [self.line_eq_from_points(p1.xy, p2.xy)
                                          for p1, p2 in polygon_lines]
        if any(self.is_point_on_line(p2, a, b, c)
               for a, b, c in polygon_lines_eqs_coefficients):
            return None
        return 0

    def get_path_from_starts_and_finishes(self, start_edges, end_points):
        # random.seed(2)
        start_edge = random.choice(list(start_edges))
        start = start_edge.target
        # random.seed(2)
        end = random.choice(list(end_points))
        start, end = start.xy, end.xy
        came_from, cost_so_far = self.a_star_search(start, end)

        path = []
        current = end
        while came_from[current] is not None:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        point_to_vert = {i.xy: i for i in self.graph.vertex_edges}
        path = [point_to_vert[i] for i in path]
        return path

    def get_river_path(self):
        start_edges = self.get_start_edges()
        end_points = self.get_end_points()
        river_path = self.get_path_from_starts_and_finishes(start_edges, end_points)
        return river_path


rg = RiverGeneration(1000, 100)
start_edges = rg.get_start_edges()
end_points = rg.get_end_points()
res = rg.get_path_from_starts_and_finishes(start_edges, end_points)


# lowest_poly_vertices = list(
#     next(groupby(sorted(rg.bounding_poly.points, key=lambda p: p.y),
#                  key=lambda x: x.y))[1])
# poly_points = lowest_poly_vertices + [lowest_poly_vertices[0]]
# polygon_lines = [(poly_points[i - 1], poly_points[i])
#                  for i in range(1, len(poly_points))]
# polygon_lines_eqs_coefficients = [rg.line_eq_from_points(p1.xy, p2.xy)
#                                   for p1, p2 in polygon_lines]
# all_p = {j for i in rg.voronoi.edges for j in (i.origin, i.twin.origin)}
# bad_point = sorted(all_p, key=lambda p: p.xy)[24]


def plot_vertices(self, vertices=None, **kwargs):
    vertices = vertices or self.voronoi.vertices

    xs = [vertex.xd for vertex in vertices]
    ys = [vertex.yd for vertex in vertices]
    if (clr := kwargs.get('color')) is None:
        color = Colors.VERTICES
    else:
        color = clr
        kwargs.pop('color')

    # Scatter points
    self.canvas.scatter(xs, ys, s=50, color=color, zorder=10, **kwargs)

    return self


Visualizer.plot_vertices = plot_vertices


Visualizer(rg.voronoi) \
    .plot_sites(show_labels=False) \
    .plot_edges(show_labels=False) \
    .plot_edges(start_edges, show_labels=False, color='red') \
    .plot_vertices() \
    .plot_vertices(end_points, color='red') \
    .plot_vertices(res, color='green') \
    .show()

# print(*sorted(j.xy for i in start_edges for j in (i.origin, i.target)))
# rg.get_start_edges_from_points({sorted((j for i in start_edges for j in (i.origin, i.target)), key=lambda p: p.xy)[0]})
# rg.get_points_on_lines({bad_point}, polygon_lines_eqs_coefficients)


# print(res)


def plot_vertices_in_line(vertices):
    x, y = zip(*[i.xy for i in vertices])
    plt.gca().set_aspect('equal')
    plt.plot(x, y)
    plt.show()


def normalize(vector):
    x, y = vector
    mag = (x ** 2 + y ** 2) ** .5
    if mag > 0:
        return x / mag, y / mag
    return vector


def vector_from_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    vector = x2 - x1, y2 - y1
    return vector


def perpendicular_counter_clockwise(vector):
    return -vector[1], vector[0]


def perpendicular_clockwise(vector):
    return vector[1], -vector[0]


def mul_vector(vector, k):
    return vector[0] * k, vector[1] * k


def offset_straight_line(start_pos, end_pos, offset):
    origin_line = start_pos, end_pos
    offset_vector = mul_vector(
        perpendicular_counter_clockwise(normalize(vector_from_points(start_pos, end_pos))), offset)
    res_line = [(x + offset_vector[0], y + offset_vector[1]) for x, y in origin_line]
    return res_line


def offset_line(line_coordinates, offset):
    pairs = zip(line_coordinates, line_coordinates[1:])
    offset_segments = (offset_straight_line(start, end, offset) for start, end in pairs)
    offset_segments = iter(offset_segments)
    start = next(offset_segments)
    yield from start
    for seg in offset_segments:
        yield from seg


def polygon_from_line(coordinates, width):
    left = offset_line(coordinates, width)
    left = list(left)
    right = offset_line(coordinates, -width)
    polygon = left + list(right)[::-1] + [left[0]]
    return polygon


# Given three collinear points p, q, r, the function checks if
# point q lies on line segment 'pr'
def is_on_segment(p, q, r):
    if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
            (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
        return True
    return False


def get_orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
    if val > 0:

        # Clockwise orientation
        return 1
    elif val < 0:

        # Counterclockwise orientation
        return 2
    else:

        # Collinear orientation
        return 0


# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.
def is_intersects(p1, q1, p2, q2):
    # Find the 4 orientations required for
    # the general and special cases
    o1 = get_orientation(p1, q1, p2)
    o2 = get_orientation(p1, q1, q2)
    o3 = get_orientation(p2, q2, p1)
    o4 = get_orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and is_on_segment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and is_on_segment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and is_on_segment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and is_on_segment(p2, q1, q2):
        return True

    # If none of the cases
    return False


def get_intersection(p1, q1, p2, q2):
    if not is_intersects(p1, q1, p2, q2):
        return None
    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    denominator = (p1[0] - q1[0]) * (p2[1] - q2[1]) - (p1[1] - q1[1]) * (p2[0] - q2[0])
    if denominator == 0:
        return float('inf')  # совпадают
    x = ((p1[0] * q1[1] - p1[1] * q1[0]) * (p2[0] - q2[0]) - (p1[0] - q1[0]) * (
            p2[0] * q2[1] - p2[1] * q2[0])) / denominator
    y = ((p1[0] * q1[1] - p1[1] * q1[0]) * (p2[1] - q2[1]) - (p1[1] - q1[1]) * (
            p2[0] * q2[1] - p2[1] * q2[0])) / denominator
    return x, y


def remove_self_intersections(polygon):
    lines = zip(polygon[::2], polygon[1::2])
    it_lines = iter(lines)
    start = next(it_lines)
    prev = start
    prev_lines = []
    for nxt in it_lines:
        intersection = get_intersection(*prev, *nxt)
        if not(intersection is None or intersection == float('inf')):
            yield from (p for ln in prev_lines for p in ln)
            prev_lines.clear()
            print(intersection)
            yield prev[0]
            yield intersection
            yield nxt[1]
            nxt = (intersection, nxt[1])
        else:
            prev_lines.append(prev)
        prev = nxt
    yield from (p for ln in prev_lines for p in ln)
    yield prev[1]
    yield start[0]


def get_poly_wo_self_intersection(polygon):
    return list(remove_self_intersections(polygon))


# line = geometry.LineString([i.xy for i in res])
# poly = geometry.Polygon(polygon_from_line([i.xy for i in res], 20))
#
# plt.gca().set_aspect('equal')
# plt.plot(*line.buffer(10).exterior.xy)
# plt.show()

# plot_vertices_in_line(res)

def main():
    Visualizer.plot_vertices = plot_vertices

    Visualizer(rg.voronoi) \
        .plot_sites(show_labels=False) \
        .plot_edges(show_labels=False) \
        .plot_edges(start_edges, show_labels=False, color='red') \
        .plot_vertices() \
        .plot_vertices(end_points, color='red') \
        .plot_vertices(res, color='green') \
        .show()

    line = [i.xy for i in res]
    poly_res = polygon_from_line(line, 30)
    print(poly_res)
    poly_repaired = get_poly_wo_self_intersection(poly_res)
    # poly_repaired = get_poly_wo_self_intersection(poly_repaired)
    poly = geometry.Polygon(poly_res)

    print(validation.explain_validity(poly))

    plt.gca().set_aspect('equal')
    plt.plot(*zip(*line))
    # plt.plot(*poly.buffer(0).exterior.xy, color='red')
    # plt.plot(*zip(*poly_res), color='red')
    plt.plot(*zip(*poly_repaired), color='green')
    plt.show()


if __name__ == '__main__':
    main()