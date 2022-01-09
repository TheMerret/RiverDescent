import math
from itertools import chain, islice, combinations
import pyclipper


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


def get_vector_normal(vector):
    i, j = vector
    magnitude = (i ** 2 + j ** 2) ** .5
    normal = (i / magnitude, j / magnitude) if magnitude > 0 else vector
    return normal


def offset_straight_line(start_pos, end_pos, offset):
    origin_line = start_pos, end_pos
    vector = vector_from_points(start_pos, end_pos)
    normal = get_vector_normal(vector)
    clockwise_normal = complex(-normal[1], normal[0])
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
    polyline_scaled = [(pyclipper.scale_to_clipper(x), pyclipper.scale_to_clipper(y))
                       for x, y in polyline]
    pco = pyclipper.PyclipperOffset()
    pco.AddPath(polyline_scaled, pyclipper.JT_MITER, pyclipper.ET_OPENBUTT)
    offset_scaled = pyclipper.scale_to_clipper(offset)
    res_scaled = pco.Execute(offset_scaled)[0]
    if res_scaled[0] != res_scaled[-1]:
        res_scaled.append(res_scaled[0])
    res = [(pyclipper.scale_from_clipper(x), pyclipper.scale_from_clipper(y))
           for x, y in res_scaled]
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


def get_angle_between_lines(line, other_line):
    vector1 = vector_from_points(*line)
    vector2 = vector_from_points(*other_line)
    dot = dot_product(vector1, vector2)
    cosine_between = dot / (vector_length(vector1) * vector_length(vector2))
    cosine_between = round(cosine_between, 14)
    angle = math.degrees(math.acos(cosine_between))
    return angle


def is_perpendicular(line, other_line):
    angle = get_angle_between_lines(line, other_line)
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
    iter_num = max(iter_num, 0)
    if iter_num == 0:
        return points
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


def get_bisect(line1, line2, bisect_length):
    # if line1[1] != line2[0]:
    #     raise ValueError('Lines must be connected')
    vec1 = vector_from_points(*line1[::-1])
    vec_norm1 = get_vector_normal(vec1)
    vec2 = vector_from_points(*line2)
    vec_norm2 = get_vector_normal(vec2)
    vec_sum = vec_norm1[0] + vec_norm2[0], vec_norm1[1] + vec_norm2[1]
    normal = get_vector_normal(vec_sum)
    bisect = normal[0] * bisect_length, normal[1] * bisect_length
    bisect = (line1[1],
              (line1[1][0] + bisect[0], line1[1][1] + bisect[1]))
    return bisect


def get_path_bisects(path, bisect_width):
    bisects = []
    lines = [line for line in zip(path, path[1:])]
    for line1, line2 in zip(lines, lines[1:]):
        right_half = get_bisect(line1, line2, bisect_width / 2)
        left_half = get_bisect(line1, line2, -bisect_width / 2)
        bisect = left_half[::-1][0], right_half[1]
        bisects.append(bisect)
    return bisects


def clip_geom_by_polygon(polygon, geom_list, geom_closed):
    pc = pyclipper.Pyclipper()
    polygon_scaled = [(pyclipper.scale_to_clipper(x), pyclipper.scale_to_clipper(y))
                      for x, y in polygon]
    pc.AddPath(polygon_scaled, pyclipper.PT_CLIP, closed=True)
    for geom in geom_list:
        geom_scaled = [(pyclipper.scale_to_clipper(x), pyclipper.scale_to_clipper(y))
                       for x, y in geom]
        if len(set(geom_scaled)) != len(geom_scaled):  # совпадающие точки
            continue
        pc.AddPath(geom_scaled, pyclipper.PT_SUBJECT, closed=geom_closed)
    res_scaled = pc.Execute2(pyclipper.CT_INTERSECTION,
                             pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    res = []
    for child in res_scaled.Childs:
        res_geom_scaled = child.Contour
        res_geom = [(pyclipper.scale_from_clipper(x), pyclipper.scale_from_clipper(y))
                    for x, y in res_geom_scaled]
        res.append(res_geom)
    return res


def clip_lines_by_polygon(polygon, lines):
    res = clip_geom_by_polygon(polygon, lines, geom_closed=False)
    return res


def get_mean_of_two_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    mean = (x1 + x2) / 2, (y1 + y2) / 2
    return mean


def get_center_line_of_two(line1, line2):
    p1, q1 = line1
    p2, q2 = line2
    center_line = get_mean_of_two_points(p1, q1), get_mean_of_two_points(p2, q2)
    return center_line


def get_distance_between_points(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** .5


def clip_lines_to_fit_rect_by_polygon(polygon, lines, rect_size):
    """Обрезаем линии по полигону, но так чтобы прямоугольник влезал"""
    rect_width, rect_height = rect_size
    fitted_lines = []
    for origin_line in lines:
        expanded_line = offset_polyline(origin_line, rect_height)
        # Строим 4 линии для прямоугольников
        expanded_lines = zip(expanded_line, expanded_line[1:])
        # Берем только параллельные линии
        expanded_lines = (line for line in expanded_lines if not is_perpendicular(line, origin_line))
        # Удленяем, чтоб наверняка пересекал реку
        expanded_lines = [resize_line_on_ends_from_center(line, rect_width * 3)
                          for line in expanded_lines]
        clipped_lines = clip_geom_by_polygon(polygon, expanded_lines, geom_closed=False)
        # варианты соедений
        try:
            line_connecting_variants = ((p1, p2)
                                        for p1 in clipped_lines[0]
                                        for p2 in clipped_lines[1])
        except IndexError:
            print((polygon, expanded_lines, clipped_lines))
            continue
        line_pairs_variants = combinations(line_connecting_variants, 2)
        # линии которое не пересекаютс есть перпендикуляры к данным
        perpendicular_line_pair = next(iter((pair for pair in line_pairs_variants
                                             if not is_intersects(*pair[0], *pair[1]))))
        center_line = get_center_line_of_two(*perpendicular_line_pair)
        fitted_lines.append(center_line)

    res_clipped_lines = clip_lines_by_polygon(polygon, fitted_lines)
    # res = [line for line in res_clipped_lines if get_distance_between_points(*line) > rect_width]
    return res_clipped_lines


def resize_line_on_ends_from_center(line, one_side_offset):
    p1, p2 = line
    center = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    left_half_vec = vector_from_points(center, p1)
    left_norm = get_vector_normal(left_half_vec)
    left_shortener_vec = left_norm[0] * one_side_offset, left_norm[1] * one_side_offset
    left_half_vec = (left_half_vec[0] + left_shortener_vec[0],
                     left_half_vec[1] + left_shortener_vec[1])
    left_half = [(center[0] + left_half_vec[0], center[1] + left_half_vec[1]), center]
    right_half_vec = vector_from_points(center, p2)
    right_norm = get_vector_normal(right_half_vec)
    right_shortener_vec = right_norm[0] * one_side_offset, right_norm[1] * one_side_offset
    right_half_vec = (right_half_vec[0] + right_shortener_vec[0],
                      right_half_vec[1] + right_shortener_vec[1])
    right_half = [center, (center[0] + right_half_vec[0], center[1] + right_half_vec[1])]
    short_line = [left_half[0], right_half[1]]
    return short_line


def get_rectangles_on_line(rectangles, line):
    res = []
    for rect in rectangles:
        rect_lines = zip(rect[::2], rect[1::2])
        intersecting_lines = [rect_line
                              for rect_line in rect_lines
                              if is_intersects(*rect_line, line)]
        if len(intersecting_lines) > 1:
            res.append(rect)
    return res