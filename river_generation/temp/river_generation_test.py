import foronoi

from river_generation.obstacles_generation import ObstaclesGeneration
from river_generation.base_river_generation import RiverGeneration, ClosingSegmentNotFound, RiverGeom
from river_generation.utils import (is_perpendicular, chaikin_smooth, get_bisect,
                                    get_closed_polyline_from_line, offset_polyline,
                                    get_polyline_wo_self_intersection, get_path_bisects,
                                    clip_lines_by_polygon, resize_line_on_ends_from_center)


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


def viz_river_generation(voronoi: foronoi.Voronoi, edges=None, points=None, path_points=None):
    foronoi.visualization.Visualizer.plot_vertices = plot_vertices

    viz = foronoi.visualization.Visualizer(voronoi) \
        .plot_sites(show_labels=False) \
        .plot_edges(show_labels=False, color='#1f77b4')
    if edges:
        viz = viz.plot_edges(edges, show_labels=False, color='red')
    if points:
        viz = viz.plot_sites(points)
    if path_points:
        viz = viz.plot_vertices(path_points, color='green')
    viz.show()
    return viz


def test_voronoi():
    rg = RiverGeneration(1000, 100)
    viz = viz_river_generation(rg.voronoi)
    viz.canvas.set_axis_off()
    viz.canvas.figure.savefig('base_voronoi.png', dpi=1200, transparent=True)
    viz.canvas.set_axis_on()


def test_path_on_voronoi():
    rg = RiverGeneration(1000, 100)
    viz = viz_river_generation(rg.voronoi)
    viz.canvas.set_axis_off()
    viz.canvas.figure.savefig('base_voronoi.png', dpi=1200, transparent=True)
    viz.canvas.set_axis_on()


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
    line1 = (478.1512445887446, 45.900432900432904), (414.21762558665046, 132.9589779245611)
    line2 = (414.21762558665046, 132.9589779245611), (435.42974107243225, 166.38927193015326)
    # line1 = (0, -1), (0, 0)
    # line2 = (0, 0), (-1, 0)
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*line1), color='green')
    plt.plot(*zip(*line2), color='red')
    test_line = get_bisect(line1, line2, 2 ** .5)
    plt.plot(*zip(*test_line))
    plt.show()


def test_path_bisects():
    import matplotlib.pyplot as plt
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, True)
    print(river_geom.path)
    perpendiculars = get_path_bisects(river_geom.path, river_geom.width * 2)
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*river_geom.path), color='green')
    for perp in perpendiculars:
        plt.plot(*zip(*perp), color='red')
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    plt.show()


def test_path_bisects_clipped():
    import matplotlib.pyplot as plt
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, True)
    print(river_geom.path)
    expand_coefficient = 3
    perpendiculars = get_path_bisects(river_geom.path, river_geom.width * expand_coefficient)
    clipped_perpendiculars = clip_lines_by_polygon(river_geom.exterior, perpendiculars)
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*river_geom.path), color='green')
    for perp in clipped_perpendiculars:
        plt.plot(*zip(*perp), color='red')
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    plt.show()


def test_clipper():
    import matplotlib.pyplot as plt

    plt.gca().set_aspect('equal')
    subj = [(923.8852050594097, 147.99444231506325), (871.1712517193947, 153.64236588720772),
            (862.3014184397163, 200.65248226950354), (766.9230769230769, 210.69230769230768),
            (759.7356115107914, 197.51528776978418), (639.5118197488304, 270.28231962570794),
            (634.6375464684015, 294.06877323420076), (576.2778603268945, 319.7796839119276),
            (552.3018549747048, 316.2377740303541), (524.6428571428571, 349.42857142857144),
            (523.7857142857143, 349.85714285714283), (446.92616033755274, 468.98945147679325),
            (433.7022700666769, 470.1669211584466), (383.03370941111723, 586.4554210236654),
            (379.8459986550101, 606.4317417619368), (323.678391959799, 612.0753768844221),
            (290.3387423935091, 624.3965517241379), (252.24456966281923, 648.6815868399527),
            (250.0275590551181, 693.6552305961754), (235.93018335684062, 723.8638928067701),
            (171.5539377057483, 771.2519625221576), (165.75, 821.0),
            (154.28546443839875, 874.5011659541391), (150.60160597309292, 876.2802000422624),
            (107.95209580838323, 997.0)]
    plt.plot(*zip(*subj), color='red')

    # pco = pyclipper.PyclipperOffset()
    # pco.AddPath(subj, pyclipper.JT_MITER, pyclipper.ET_OPENBUTT)
    #
    # solution = pco.Execute(20)[0]

    solution = offset_polyline(subj, 20)
    plt.plot(*zip(*solution), color='green')
    plt.show()


def test_short_lines_for_obstacles():
    import matplotlib.pyplot as plt
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, True)
    print(river_geom.path)
    expand_coefficient = 3
    perpendiculars = get_path_bisects(river_geom.path, river_geom.width * expand_coefficient)
    clipped_perpendiculars = clip_lines_by_polygon(river_geom.exterior, perpendiculars)
    obstacle_width, obstacle_height = 5, 5
    shorten_delta = (obstacle_width ** 2 + obstacle_height ** 2) ** .5
    shorten_perpendiculars = [resize_line_on_ends_from_center(i, -shorten_delta)
                              for i in clipped_perpendiculars]
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*river_geom.path), color='green')
    for perp in shorten_perpendiculars:
        plt.plot(*zip(*perp), color='red')
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    plt.show()


def test_bisect_allocation():
    import matplotlib.pyplot as plt
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, True)
    plt.gca().set_aspect('equal')
    plt.plot(*zip(*river_geom.path), color='green')
    og = ObstaclesGeneration(river_geom)
    control_lines = og.get_rectangular_control_lines()
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    for line in og.control_lines:
        plt.plot(*zip(*line), color='red')
    for line in control_lines:
        plt.plot(*zip(*line), color='orange')
    plt.show()


def test_obstacle_boxes():
    import matplotlib.pyplot as plt
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, True)
    plt.gca().set_aspect('equal')
    og = ObstaclesGeneration(river_geom)
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    for line in og.control_lines:
        plt.plot(*zip(*line), color='orange')
    obstacle_boxes_groups = og.get_obstacle_groups()
    for group in obstacle_boxes_groups:
        for box in group.obstacles:
            plt.plot(*zip(*box.normalized_rect), color='red')
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
    test_voronoi()
