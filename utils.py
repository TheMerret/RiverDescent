import math
from clipper.clipper import OffsetPolyLines, Point, JoinType, EndType


def catmull_rom2bezier_svg(points, close=False):
    k = 8  # roughness
    points = [j for i in points for j in i]
    i_len = len(points)
    points.extend([0, 0, 0, 0, 0, 0])
    d = []
    i = -2
    while i_len - 2 * (not close) > i:
        i += 2
        try:
            p = [[points[i - 2], points[i - 1]],
                 [points[i], points[i + 1]],
                 [points[i + 2], points[i + 3]],
                 [points[i + 4], points[i + 5]]]
        except IndexError:
            break
        if close:
            if not i:
                p[0] = [points[i_len - 2], points[i_len - 1]]
            elif i_len - 4 == i:
                p[3] = [points[0], points[1]]
            elif i_len - 2 == i:
                p[2] = [points[0], points[1]]
                p[3] = [points[2], points[3]]
        else:
            if i_len - 4 == i:
                p[3] = p[2]
            elif not i:
                p[0] = [points[i], points[i + 1]]

        bp = [
            'C',
            (-p[0][0] + k * p[1][0] + p[2][0]) / k,
            (-p[0][1] + k * p[1][1] + p[2][1]) / k,
            (p[1][0] + k * p[2][0] - p[3][0]) / k,
            (p[1][1] + k * p[2][1] - p[3][1]) / k,
            p[2][0],
            p[2][1]
        ]

        d.append(bp)

    return d[:-1]


def get_svg_paths(bezier_curves):
    svg_paths = []
    for curve in bezier_curves:
        curve_type, x1, y1, x2, y2, x, y = curve
        svg_path = f"{curve_type} {x1} {y1}, {x2} {y2}, {x} {y}"
        svg_paths.append(svg_path)
    return svg_paths


def get_curved_svg_from_points(points, color='red', closed=False):
    svg = """  
<svg viewBox="{} {} {} {}" xmlns="http://www.w3.org/2000/svg">
    <path d="{}" stroke="{}" fill="none" stroke-width="1%" transform="scale(1, -1)" 
    transform-origin="center"/>
</svg>
"""
    svg = svg.strip()
    max_x = max(i[0] for i in points)
    min_x = min(i[0] for i in points)
    max_y = max(i[1] for i in points)
    min_y = min(i[1] for i in points)
    width = max_x - min_x
    height = max_y - min_y
    start_point = f'M {points[0][0]} {points[0][1]} '
    paths_commands = catmull_rom2bezier_svg(points, closed)
    path = ' '.join(get_svg_paths(paths_commands))
    path = start_point + path
    svg = svg.format(min_x, abs(min_y), width, height, path, color)  # abs так отражаем по y
    return svg


def save_smooth_svg_from_points(points, save_path, color='red', closed=False):
    svg = get_curved_svg_from_points(points, color=color, closed=closed)
    with open(save_path, 'w') as f:
        f.write(svg)


def offset_straight_line(start_pos, end_pos, offset):
    origin_line = start_pos, end_pos
    vector = complex(*end_pos) - complex(*start_pos)
    i, j = vector.real, vector.imag
    magnitude = (i ** 2 + j ** 2) ** .5
    normal = complex(i / magnitude, j / magnitude) if magnitude > 0 else vector
    clockwise_normal = complex(-normal.imag, normal.real)
    offset_vector = clockwise_normal * offset
    res_line = [(x + offset_vector.real, y + offset_vector.imag) for x, y in origin_line]
    return res_line


def offset_line(line_coordinates, offset):
    pairs = zip(line_coordinates, line_coordinates[1:])
    offset_segments = (offset_straight_line(start, end, offset) for start, end in pairs)
    offset_segments = iter(offset_segments)
    start = next(offset_segments)
    yield from start
    for seg in offset_segments:
        yield from seg


def get_closed_polyline_from_line(coordinates, width):
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

    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
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


def get_polyline_wo_self_intersection(polyline):
    lines = list(zip(polyline, polyline[1:]))
    latest = lines[-1]
    latest_ind = len(lines) - 1
    lines = [latest] + lines[:-1] + [latest]
    res = []
    lines_iter = enumerate(lines)
    skip_indexes = []
    for ind_line, line in lines_iter:
        cur_intersection = None
        skip = False
        for skip_ind, skip_value in skip_indexes:
            if skip_ind == ind_line:
                skip = skip_value
        if skip is None:
            continue
        if skip:
            line = (skip, line[1])
        for other_ind, other_line in enumerate(lines[ind_line + 2:], ind_line + 2):
            two_line_points = (*line, *other_line)
            two_line_points = [(round(a, 10), round(b, 10)) for a, b in two_line_points]
            intersection = get_intersection(*two_line_points)
            if (intersection is not None
                    and intersection != float('inf')):
                intersection = tuple(map(lambda num: round(num, 10), intersection))
                if intersection not in two_line_points and other_ind != latest_ind + 1:
                    if line == latest:
                        if other_ind > (latest_ind + 1) // 2:
                            line = None
                            break
                        skip_indexes.append((latest_ind + 1, None))
                    cur_intersection = (intersection, two_line_points[-1]), other_ind
        if not res:
            if line is not None:
                res.append(line[0])
        if cur_intersection is not None:
            res.append(cur_intersection[0][0])
            for i in range(ind_line, cur_intersection[1]):
                skip_indexes.append((i, None))
            skip_indexes.append((cur_intersection[1], cur_intersection[0][0]))
        else:
            if line is not None:
                res.append(line[1])
    return res[::-1]


def offset_polyline(polyline, offset):
    polyline = [[Point(*i) for i in polyline]]
    res = OffsetPolyLines(polyline, offset, jointype=JoinType.Miter, endtype=EndType.Butt)[0]
    res = [(i.x, i.y) for i in res]
    if res[0] != res[-1]:
        res.append(res[0])
    return res


def vector_from_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    vector = x2 - x1, y2 - y1
    return vector


def dot_product(v1, v2):
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    return dot


def vector_length(vector):
    length = (vector[0] ** 2 + vector[1] ** 2) ** .5
    return length


def is_perpendicular(line, other_line):
    vector1 = vector_from_points(*line)
    vector2 = vector_from_points(*other_line)
    dot = dot_product(vector1, vector2)
    cosine_between = dot / (vector_length(vector1) * vector_length(vector2))
    cosine_between = round(cosine_between, 14)
    angle = math.degrees(math.acos(cosine_between))
    angle = round(int(angle) + 1, -1)
    return angle == 90


def get_q_point(p1, p2, percent):
    cut_p1 = p1[0] * (1 - percent), p1[1] * (1 - percent)
    cut_p2 = p2[0] * percent, p2[1] * percent
    q_point = cut_p1[0] + cut_p2[0], cut_p1[1] + cut_p2[1]
    return q_point


def get_r_point(p1, p2, percent):
    cut_p1 = p1[0] * percent, p1[1] * percent
    cut_p2 = p2[0] * (1 - percent), p2[1] * (1 - percent)
    r_point = cut_p1[0] + cut_p2[0], cut_p1[1] + cut_p2[1]
    return r_point


def chaikin_smooth(points, iter_num=1, percent=0.25, closed=False):
    iter_num = max(iter_num, 1)
    percent = max(min(percent, 1), 0)

    smoothed_points = []
    if not closed:
        smoothed_points.append(points[0])

    for ind, i in enumerate(points):
        p1 = i
        try:
            p2 = points[ind + 1]
        except IndexError:
            if not closed:
                smoothed_points.append(p1)
            continue
        q_point = get_q_point(p1, p2, percent)
        r_point = get_r_point(p1, p2, percent)

        smoothed_points.append(q_point)
        smoothed_points.append(r_point)

    if closed:
        smoothed_points.append(smoothed_points[0])

    if iter_num == 1:
        return smoothed_points
    return chaikin_smooth(smoothed_points, iter_num - 1, percent, closed)