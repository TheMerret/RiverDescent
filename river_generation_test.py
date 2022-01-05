import math

import foronoi

from utils import (is_perpendicular, chaikin_smooth, get_bisect,
                   get_closed_polyline_from_line, offset_polyline,
                   get_polyline_wo_self_intersection)
from river_generation import RiverGeneration, ClosingSegmentNotFound, RiverGeom


def plot_vertices(self, vertices=None, **kwargs):
    vertices = vertices or self.voronoi.vertices

    xs = [vertex.xd for vertex in vertices]
    ys = [vertex.yd for vertex in vertices]
    if (clr := kwargs.get('color')) is None:
        color = foronoi.visualization.visualizer.Colors.VERTICES
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


def viz_river_generation(voronoi: foronoi.Voronoi, edges, points, path_points=None):
    foronoi.visualization.Visualizer.plot_vertices = plot_vertices

    viz = foronoi.visualization.Visualizer(voronoi) \
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


def test_bisect():
    import matplotlib.pyplot as plt
    line1 = (370.0832546006841, 100.45889030941743), (317.49618206629873, 167.5766013072514)
    line2 = (317.49618206629873, 167.5766013072514), (316.2397901488098, 190.44775216640403)
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*line1), color='green')
    plt.plot(*zip(*line2), color='red')
    test_line = get_bisect(line1, line2, 100)
    plt.plot(*zip(*test_line))
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
    plt.gca().set_axis_off()
    plt.savefig('river_test.svg', format='svg')
    plt.gca().set_axis_on()
    plt.show()


if __name__ == '__main__':
    test_bisect()