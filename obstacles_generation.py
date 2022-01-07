from itertools import chain, islice

from river_generation import RiverGeom
from utils import get_path_bisects, clip_lines_by_polygon, chaikin_smooth, is_intersects

OBSTACLE_SIZE = (5, 5)
BOAT_SIZE = (10, 30)  # FIXME: с маленькими размерами Pyclipper выдает ошибку
MIN_BUFF_COEFFICIENT = 1.5  # минимальное расстояние между препятствиями, относительно длины лодки
min_buff = BOAT_SIZE[1] * MIN_BUFF_COEFFICIENT
# Это коефициент сглаживания.
CONTROL_LINES_COEFFICIENT = 3  # Можно увеличить количество конторольных линий, сгладив линию реки


class ObstaclesGeneration:

    def __init__(self, river_geometry: RiverGeom):
        self.river_geometry = river_geometry
        self.control_lines = self.get_control_lines()

    def get_river_bisects(self):
        expand_coefficient = 3  # для уверрности, что линии пересекают берега
        bisect_count_coefficient = 5  # можно увеличить количество конторольных линий, сгладив
        # линию реки
        river_path = chaikin_smooth(self.river_geometry.path, bisect_count_coefficient)
        raw_bisects = get_path_bisects(river_path,
                                       self.river_geometry.width * expand_coefficient)
        clipped_bisects = clip_lines_by_polygon(self.river_geometry.exterior, raw_bisects)
        return clipped_bisects

    def allocate_control_lines_gen(self, lines):
        # сверху вниз двигаемся
        valid_indexes = {0}
        start_segment = self.river_geometry.top_segment
        for cur_ind, current_line in enumerate(chain((start_segment,), lines)):
            if cur_ind not in valid_indexes:
                continue
            yield current_line
            for other_ind, next_line in enumerate(islice(chain((start_segment,), lines),
                                                         cur_ind + 1, None, 1), cur_ind + 1):
                distance = self.get_min_distance_between_segments(current_line, next_line)
                if distance >= min_buff and not is_intersects(*current_line, *next_line):
                    valid_indexes.add(other_ind)
                    break

    @staticmethod
    def get_min_distance_between_segments(line, other_line):
        get_distance_between_points = (lambda p1, p2: ((p2[0] - p1[0]) ** 2
                                                       + (p2[1] - p1[1]) ** 2) ** .5)
        min_distance_between_segments = min((get_distance_between_points(p1, p2)
                                             for p1 in line for p2 in other_line))
        return min_distance_between_segments

    def get_control_lines(self):
        control_lines = self.get_river_bisects()
        control_lines = list(self.allocate_control_lines_gen(control_lines))
        last_control_line = control_lines.pop()
        # если последняя контрольная линия и низ реки создают слишком мало места для
        # лодки, то мы удаляем эту контрольную линию
        if self.get_min_distance_between_segments(self.river_geometry.bottom_segment,
                                                  last_control_line) > min_buff:
            control_lines.append(last_control_line)
        return control_lines
