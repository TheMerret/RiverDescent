from typing import List
import json

from river_generation import RiverGeom, ObstacleGroup, ObstacleGeom


def save_river_data(river_geom: RiverGeom, obstacle_groups: List[ObstacleGroup], save_path):
    save_data = {
        'river_geom':
            {
                'path': [],
                'exterior': [],
            },
        'obstacle_groups': [
            {
                'control_line': [],
                'obstacles': [],
            }
        ]
    }

    save_data['river_geom']['path'] = river_geom.path
    save_data['river_geom']['exterior'] = river_geom.exterior

    obstacle_groups_save_data = [
        {'control_line':
             group.control_line,
         'obstacles': [obstacle.original_rect for obstacle in group.obstacles]} for group in obstacle_groups
    ]
    save_data['obstacle_groups'] = obstacle_groups_save_data

    with open(save_path, 'w', encoding='utf-8') as fd:
        json.dump(save_data, fd)


def load_river_data(load_path) -> (RiverGeom, List[ObstacleGroup]):
    with open(load_path, 'r', encoding='utf-8') as fd:
        raw_data = json.load(fd)
    river_geom_data = raw_data['river_geom']
    river_geom = RiverGeom(river_geom_data['path'], river_geom_data['exterior'], smooth=False)
    obstacle_groups_data = raw_data['obstacle_groups']
    obstacle_groups = [
        ObstacleGroup(
            [ObstacleGeom(rect) for rect in group['obstacles']],
            group['control_line']
        ) for group in obstacle_groups_data
    ]
    return river_geom, obstacle_groups
