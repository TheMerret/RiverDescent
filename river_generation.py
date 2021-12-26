from itertools import groupby
from typing import List, Dict, Set
import heapq
import random

import foronoi
import numpy as np
from foronoi import Voronoi, Polygon, Visualizer, Point, VoronoiObserver
from foronoi.visualization.visualizer import Colors
from foronoi.graph import HalfEdge, Vertex

from utils import get_closed_polyline_from_line, get_polyline_wo_self_intersection, offset_polyline, \
    is_perpendicular, chaikin_smooth


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
            return float('inf')
        return 0

    def get_start_and_end_path_variants(self):
        start_edges = self.get_start_edges()
        end_points = self.get_end_points()
        return start_edges, end_points

    @staticmethod
    def get_start_and_end_from_variants(start_end_variants):
        start_edges, end_points = start_end_variants
        # random.seed(2)
        start_edge = random.choice(list(start_edges))
        start = start_edge.target
        # random.seed(2)
        end = random.choice(list(end_points))
        return start, end

    def get_start_and_end(self):
        start_end_variants = self.get_start_and_end_path_variants()
        start, end = self.get_start_and_end_from_variants(start_end_variants)
        return start, end

    def get_path_from_start_and_end(self, start, end, as_vertices=False):
        start, end = start.xy, end.xy
        came_from, cost_so_far = self.a_star_search(start, end)

        path = []
        current = end
        while came_from[current] is not None:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        if as_vertices:
            point_to_vert = {i.xy: i for i in self.graph.vertex_edges}
            path = [point_to_vert[i] for i in path]
        return path

    def get_river_path(self):
        start, end = self.get_start_and_end()
        river_path = self.get_path_from_start_and_end(start, end)
        return river_path

    @staticmethod
    def get_expanded_river_exterior_from_path(river_path, width):
        exterior = get_closed_polyline_from_line(river_path, width)
        exterior = get_polyline_wo_self_intersection(exterior)
        return exterior

    @staticmethod
    def get_expanded_river_exterior_from_path2(river_path, width):
        exterior = offset_polyline(river_path, width)
        return exterior

    def get_river_exterior(self, width):
        river_path = self.get_river_path()
        river_exterior = self.get_expanded_river_exterior_from_path2(river_path, width)
        return river_exterior

    @staticmethod
    def get_river_geom_from_path_and_exterior(river_path, river_exterior, smooth=False):
        river_geom = RiverGeom(river_path, river_exterior, smooth=smooth)
        return river_geom

    def get_river_geom(self, exterior_width, smooth=False):
        river_path = self.get_river_path()
        river_exterior = self.get_expanded_river_exterior_from_path2(river_path, exterior_width)
        river_geom = self.get_river_geom_from_path_and_exterior(river_path, river_exterior,
                                                                smooth=smooth)
        return river_geom


class ClosingSegmentNotFound(Exception):
    pass


class RiverGeom:

    def __init__(self, river_path, river_exterior, *, smooth=False):
        self.path = river_path
        self.exterior = river_exterior
        (self.bottom_segment, self.right_bank,
         self.top_segment, self.left_bank) = self.split_exterior()
        self.origin_exterior = (list(self.bottom_segment)
                                + self.right_bank
                                + list(self.top_segment)
                                + self.left_bank)
        if smooth:
            self.smooth_banks()
        self.exterior = (list(self.bottom_segment)
                         + self.right_bank
                         + list(self.top_segment)
                         + self.left_bank)

    def get_closing_segments(self):
        first_segment_start, first_segment_end, *_, last_segment_start, last_segment_end = self.path
        first_segment = first_segment_start, first_segment_end
        last_segment = last_segment_start, last_segment_end
        get_min_y = (lambda ln: min(i[1] for i in ln))
        get_max_y = (lambda ln: max(i[1] for i in ln))
        closing_exterior_segments = [(float('inf'),
                                      ((float('inf'), float('inf')),
                                       (float('inf'), float('inf')))),
                                     (float('-inf'),
                                      ((float('-inf'), float('-inf')),
                                       (float('-inf'), float('-inf'))))]
        for ind, segment in enumerate(zip(self.exterior, self.exterior[1:])):
            if is_perpendicular(segment, first_segment):
                if get_min_y(segment) < get_min_y(closing_exterior_segments[0][1]):
                    closing_exterior_segments[0] = (ind, segment)
            if is_perpendicular(segment, last_segment):
                if get_max_y(segment) > get_max_y(closing_exterior_segments[1][1]):
                    closing_exterior_segments[1] = (ind, segment)
        if (closing_exterior_segments[0][0] == float('inf')
                or closing_exterior_segments[1][0] == float('-inf')):
            raise ClosingSegmentNotFound
        return closing_exterior_segments

    def split_exterior(self):
        ((bottom_segment_ind, bottom_segment),
         (top_segment_ind, top_segment)) = self.get_closing_segments()
        left_bank = []
        left_bank_last = []
        right_bank = []
        right_bank_last = []
        cur_mode = 0 if bottom_segment_ind < top_segment_ind else 1  # 0 - left, 1 - right
        right_left_append = False
        left_left_append = False
        for ind, seg in enumerate(zip(self.exterior, self.exterior[1:])):
            if cur_mode == 0:
                if ind == bottom_segment_ind:
                    cur_mode = 1
                    left_left_append = True
                    continue
                if left_left_append:
                    left_bank_last.append(seg)
                else:
                    left_bank.append(seg)
            else:
                if ind == top_segment_ind:
                    cur_mode = 0
                    right_left_append = True
                    continue
                if right_left_append:
                    right_bank_last.append(seg)
                else:
                    right_bank.append(seg)
        left_bank = left_bank_last + left_bank
        left_bank = iter(left_bank)
        left_bank = list(next(left_bank)) + [i[1] for i in left_bank]
        right_bank = right_bank_last + right_bank
        right_bank = iter(right_bank)
        right_bank = list(next(right_bank)) + [i[1] for i in right_bank]
        return list(bottom_segment), right_bank, list(top_segment), left_bank

    def smooth_banks(self):
        self.right_bank = chaikin_smooth(self.right_bank, 5)
        self.left_bank = chaikin_smooth(self.left_bank, 5)


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


def plot_vertices_in_line(vertices):
    import matplotlib.pyplot as plt
    x, y = zip(*[i.xy for i in vertices])
    plt.gca().set_aspect('equal')
    plt.plot(x, y)
    plt.show()


# line = geometry.LineString([i.xy for i in res])
# poly = geometry.Polygon(polygon_from_line([i.xy for i in res], 20))
#
# plt.gca().set_aspect('equal')
# plt.plot(*line.buffer(10).exterior.xy)
# plt.show()

# plot_vertices_in_line(res)

def viz_river_generation(voronoi: Voronoi, edges, points, path_points=None):
    Visualizer.plot_vertices = plot_vertices

    viz = Visualizer(voronoi) \
        .plot_sites(show_labels=False) \
        .plot_edges(show_labels=False) \
        .plot_edges(edges, show_labels=False, color='red') \
        .plot_vertices() \
        .plot_vertices(points, color='red')
    if path_points:
        viz = viz.plot_vertices(path_points, color='green')
    viz.show()


def test_perpendicular():
    import matplotlib.pyplot as plt
    line1 = (553.7137223974763, 64.40496845425868), (587.873246492986, 64.11548096192385)
    line2 = ((554, 83), (554, 44))
    print(is_perpendicular(line1, line2))
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*line1), color='green')
    plt.plot(*zip(*line2), color='red')
    plt.show()


def test_smooth():
    import matplotlib.pyplot as plt
    line = [(824.2087378640776, 53.79126213592233), (853.7946486839243, 146.09930389384382),
            (862.2424218251435, 151.46478142948308), (871.1128500823723, 201.29571663920922),
            (872.2550241565507, 211.4195322966993), (815.545835618585, 270.6379769646635),
            (797.4654210410396, 276.51123265545846), (751.1875, 371.84375),
            (760.6363636363636, 414.3636363636364), (737.6612903225806, 437.33870967741933),
            (710.5110375275938, 457.5331125827815), (707.8575371549894, 457.80573248407643),
            (613.5594683886469, 492.0268058267007), (605.7566071242035, 561.0205264807271),
            (563.1470588235294, 567.6323529411765), (531.3928571428571, 647.0178571428571),
            (504.0, 638.8), (457.4072657743786, 694.7112810707457),
            (467.9822485207101, 707.7455621301775), (447.50699558173784, 798.7466863033874),
            (452.320308935671, 843.3792283125855), (340.36961907711367, 874.8174357386188),
            (340.34295273943957, 874.836051861146), (328.0153206390895, 962.8905668636463),
            (294.2473512632437, 956.4405052974735), (164.58881510686865, 970.5338244449056),
            (165.16136919315403, 979.0403422982885), (233.00000000000003, 996.0)]
    res = chaikin_smooth(line, 5, closed=False)
    plt.gca().set_aspect('equal')
    # plt.plot(*zip(*line), color='green')
    plt.plot(*zip(*res), color='red')
    plt.show()


def main():
    from shapely import geometry, validation
    import matplotlib.pyplot as plt

    rg = RiverGeneration(1000, 100)
    start_edges = rg.get_start_edges()
    end_points = rg.get_end_points()
    start, end = rg.get_start_and_end_from_variants((start_edges, end_points))
    river_path = rg.get_path_from_start_and_end(start, end)

    # viz_river_generation(rg.voronoi, start_edges, end_points, river_path)

    # river_path = [(824.2087378640776, 53.79126213592233), (853.7946486839243, 146.09930389384382),
    #               (862.2424218251435, 151.46478142948308), (871.1128500823723, 201.29571663920922),
    #               (872.2550241565507, 211.4195322966993), (815.545835618585, 270.6379769646635),
    #               (797.4654210410396, 276.51123265545846), (751.1875, 371.84375),
    #               (760.6363636363636, 414.3636363636364), (737.6612903225806, 437.33870967741933),
    #               (710.5110375275938, 457.5331125827815), (707.8575371549894, 457.80573248407643),
    #               (613.5594683886469, 492.0268058267007), (605.7566071242035, 561.0205264807271),
    #               (563.1470588235294, 567.6323529411765), (531.3928571428571, 647.0178571428571),
    #               (504.0, 638.8), (457.4072657743786, 694.7112810707457),
    #               (467.9822485207101, 707.7455621301775), (447.50699558173784, 798.7466863033874),
    #               (452.320308935671, 843.3792283125855), (340.36961907711367, 874.8174357386188),
    #               (340.34295273943957, 874.836051861146), (328.0153206390895, 962.8905668636463),
    #               (294.2473512632437, 956.4405052974735), (164.58881510686865, 970.5338244449056),
    #               (165.16136919315403, 979.0403422982885), (233.00000000000003, 996.0)]

    raw_river_polyline = get_closed_polyline_from_line(river_path, 20)
    print(raw_river_polyline)
    river_polyline_repaired = get_polyline_wo_self_intersection(raw_river_polyline)
    # river_polyline_repaired = [(650.0050442508174, 102.08098053052966),
    #                            (652.1867584772918, 108.35340893164364),
    #                            (652.9105374339, 101.070374206),
    #                            (650.0050442508174, 102.08098053052966)]
    poly = geometry.Polygon(river_polyline_repaired)
    print(validation.explain_validity(poly))

    plt.gca().set_aspect('equal')
    plt.plot(*zip(*river_path))
    # plt.plot(*poly.buffer(0).exterior.xy, color='red')
    # plt.plot(*zip(*poly_res), color='red')

    # plt.plot(*zip(*river_polyline_repaired), color='green')

    try:
        river_exterior2 = offset_polyline(river_path, 20)
    except AttributeError:
        print('error attribute')
        river_exterior2 = None
    else:
        poly = geometry.Polygon(river_exterior2)
        print(validation.explain_validity(poly))
        plt.plot(*zip(*river_exterior2), color='green')

    try:
        if river_exterior2 is None:
            raise ClosingSegmentNotFound
        river_geom = RiverGeom(river_path, river_exterior2, smooth=True)
    except ClosingSegmentNotFound:
        print('error')
    else:
        print(river_geom)
        poly = geometry.Polygon(river_geom.exterior)
        print(validation.explain_validity(poly))

        plt.plot(*zip(*river_geom.exterior), color='red')
        # plt.plot(*zip(*river_geom.left_bank), color='red')
        # plt.plot(*zip(*river_geom.bottom_segment), color='green')
        # plt.plot(*zip(*river_geom.right_bank), color='blue')
        # plt.plot(*zip(*river_geom.top_segment), color='magenta')
    plt.show()


if __name__ == '__main__':
    main()
