import xml.etree.ElementTree as ET
from svgpathtools import parse_path, Line, Path, wsvg, smoothed_path
from river_generation import RiverGeneration
from utils import get_curved_svg_from_points
from main import get_river_exterior


def offset_curve(path, offset_distance, steps=1000):
    """Takes in a Path object, `path`, and a distance,
    `offset_distance`, and outputs an piecewise-linear approximation
    of the 'parallel' offset curve."""
    nls = []
    for seg in path:
        ct = 1
        for k in range(steps):
            t = k / steps
            offset_vector = offset_distance * seg.normal(t)
            nl = Line(seg.point(t), seg.point(t) + offset_vector)
            nls.append(nl)
    connect_the_dots = [Line(nls[k].end, nls[k + 1].end) for k in range(len(nls) - 1)]
    if path.isclosed():
        connect_the_dots.append(Line(nls[-1].end, nls[0].end))
    offset_path = Path(*connect_the_dots)
    return offset_path


def river_smooth_svg():
    rg = RiverGeneration(1000, 100)
    river_path = rg.get_river_path()
    river_path = [i.xy for i in river_path]
    river_exterior = rg.get_expanded_river_exterior_from_path2(river_path, 20)
    res = None
    if len(river_exterior) < 10:
        print(river_path)
        print(river_exterior)
        res = True
    curved_river_svg = get_curved_svg_from_points(river_exterior)
    root = ET.fromstring(curved_river_svg)
    svg_path = root[0].attrib['d']
    svg_path = parse_path(svg_path)
    # lines = list(zip(river_exterior, river_exterior[1:]))
    # svg_path = Path(*(Line(complex(*a), complex(*b)) for a, b in lines))
    # try:
    #     svg_path = smoothed_path(svg_path, 5, 1.999999999)
    # except Exception:
    #     print(river_exterior)
    # offset_path = offset_curve(svg_path, -10)

    # Let's take a look
    wsvg([svg_path, ], 'r', filename='offset_curve.svg')
    return res


def test_error_river():
    while True:
        res = river_smooth_svg()
        if res:
            break


if __name__ == '__main__':
    river_smooth_svg()