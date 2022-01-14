from itertools import chain, islice
from random import choice
from typing import List

from river_generation.base_river_generation import RiverGeom
from river_generation.utils import (get_path_bisects, clip_lines_by_polygon,
                                    chaikin_smooth, is_intersects, clip_lines_to_fit_rect_by_polygon,
                                    get_distance_between_points, get_vector_normal,
                                    vector_from_points, get_angle_between_lines,
                                    offset_polyline, get_rectangles_on_line, get_center_line_of_two,
                                    rotate_polygon, get_mean_of_two_points)

OBSTACLE_SIZE = (100, 100)
BOAT_SIZE = (270, 400)  # FIXME: с маленькими размерами Pyclipper выдает ошибку
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
        river_path = chaikin_smooth(self.river_geometry.path, CONTROL_LINES_COEFFICIENT)
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
            # самый верх реки не нужен как контрольная линия
            if cur_ind != 0:
                yield current_line
            for other_ind, next_line in enumerate(islice(chain((start_segment,), lines),
                                                         cur_ind + 1, None, 1), cur_ind + 1):
                distance = self.get_min_distance_between_segments(current_line, next_line)
                if distance >= min_buff and not is_intersects(*current_line, *next_line):
                    valid_indexes.add(other_ind)
                    break

    @staticmethod
    def get_min_distance_between_segments(line, other_line):
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

    def get_rectangular_control_lines(self):
        """Убираем некоторые по бокам препятсвия чтоб лодка развернулась"""
        res = clip_lines_to_fit_rect_by_polygon(self.river_geometry.exterior,
                                                self.control_lines,
                                                (BOAT_SIZE[0] * 2, BOAT_SIZE[1]))
        return res

    def get_obstacle_groups(self):
        res = []
        obstacles_boxes = (self.get_obstacle_boxes_on_line(control_line)
                           for control_line in self.control_lines)
        for (obstacles_boxes_on_line,
             shorten_control_line,
             control_line) in zip(obstacles_boxes,
                                  self.get_rectangular_control_lines(),
                                  self.control_lines):
            shorten_obstacles = get_rectangles_on_line(obstacles_boxes_on_line,
                                                       shorten_control_line)
            obstacles_wo_boat = self.get_obstacles_with_rect_buffer(
                shorten_obstacles,
                obstacles_boxes_on_line,
                (BOAT_SIZE[0] * 1.5, BOAT_SIZE[1])
            )
            obstacle_group = ObstacleGroup([ObstacleGeom(i) for i in obstacles_wo_boat],
                                           control_line)
            res.append(obstacle_group)
        return res

    def get_obstacles_boxes(self):
        obstacle_groups = self.get_obstacle_groups()
        res = []
        for group in obstacle_groups:
            for obstacle in group.obstacles:
                res.append(obstacle.original_rect)
        return res

    @staticmethod
    def get_obstacle_boxes_on_line(line):
        line_length = get_distance_between_points(*line)
        obstacle_count = int(line_length // OBSTACLE_SIZE[0])
        try:
            delta = line_length / obstacle_count
        except ZeroDivisionError:
            # FIXME: странно что он не насчитал препятствий
            return []
        line_normal = get_vector_normal(vector_from_points(*line))
        obstacle_center_lines = []
        base_point = line[0]
        for _ in range(obstacle_count):
            obstacle_vector = line_normal[0] * OBSTACLE_SIZE[0], line_normal[1] * OBSTACLE_SIZE[1]
            obstacle_segment = (base_point, (base_point[0] + obstacle_vector[0],
                                             base_point[1] + obstacle_vector[1]))
            obstacle_center_lines.append(obstacle_segment)
            delta_vector = line_normal[0] * delta, line_normal[1] * delta
            base_point = (base_point[0] + delta_vector[0], base_point[1] + delta_vector[1])
        obstacle_boxes = [offset_polyline(line, OBSTACLE_SIZE[1] / 2)
                          for line in obstacle_center_lines]
        return obstacle_boxes

    @staticmethod
    def get_obstacles_with_rect_buffer(shorten_obstacle_boxes, original_obstacle_boxes, rect_size):
        """Расчищаем препятсвия так, чтобы лодка влезала"""
        box_count_for_rect = int(rect_size[0] // OBSTACLE_SIZE[0]) + 1
        try:
            start_ind, start_box = choice(
                list(enumerate(shorten_obstacle_boxes[:-(box_count_for_rect - 1)]))
            )
        except IndexError:
            # print(shorten_obstacle_boxes)
            return []
        buffer_boxes = shorten_obstacle_boxes[start_ind:start_ind + box_count_for_rect]
        res = []
        for box in original_obstacle_boxes:
            if box in buffer_boxes:
                continue
            res.append(box)
        return res


class ObstacleGeom:

    def __init__(self, obstacle_coordinates):
        if len(obstacle_coordinates) != 4 + 1 or obstacle_coordinates[0] != obstacle_coordinates[-1]:
            raise ValueError('obstacle coordinates should represent rectangle')
        self.original_rect = obstacle_coordinates
        parallel_lines = ((self.original_rect[0], self.original_rect[1]),
                          (self.original_rect[2], self.original_rect[3]))
        self.center_line = get_center_line_of_two(*parallel_lines)
        self.rotate_degree = get_angle_between_lines(self.center_line, ((0, 0), (1, 0)))
        self.center = get_mean_of_two_points(*self.center_line)
        self.normalized_rect = rotate_polygon(self.original_rect, self.rotate_degree, self.center)
        width = get_distance_between_points(self.normalized_rect[0], self.normalized_rect[1])
        height = get_distance_between_points(self.normalized_rect[1], self.normalized_rect[2])
        self.size = width, height


class ObstacleGroup:

    def __init__(self, obstacles: List[ObstacleGeom], control_line):
        self.obstacles = obstacles
        self.control_line = control_line
