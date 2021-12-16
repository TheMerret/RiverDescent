def catmull_rom2bezier_svg(points, close=False):
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
            (-p[0][0] + 6 * p[1][0] + p[2][0]) / 6,
            (-p[0][1] + 6 * p[1][1] + p[2][1]) / 6,
            (p[1][0] + 6 * p[2][0] - p[3][0]) / 6,
            (p[1][1] + 6 * p[2][1] - p[3][1]) / 6,
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