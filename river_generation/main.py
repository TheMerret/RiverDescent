from river_generation.river_generation import RiverGeneration
from river_generation.obstacles_generation import ObstaclesGeneration


def get_river_path():
    rg = RiverGeneration(1000, 100)
    river_path = rg.get_river_path()
    river_path = [i.xy for i in river_path]
    return river_path


def get_river_exterior():
    rg = RiverGeneration(1000, 100)
    river_exterior = rg.get_river_exterior(20)
    return river_exterior


def get_river_geometry():
    """Возвращает объект геометрии реки с разделенным правым и левым берегом"""
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, smooth=True)
    # river_geom.right_bank - правый берег
    return river_geom


def get_river_obstacles():
    rg = RiverGeneration(1000, 100)
    river_geom = rg.get_river_geom(20, smooth=True)
    og = ObstaclesGeneration(river_geom)
    # группа есть линия последовательных препятствий на одной линии
    obstacle_groups = og.get_obstacle_groups()
    obstacles = [obstacle for obstacle_group in obstacle_groups for obstacle
                 in obstacle_group.obstacles]
    # obstacle = obstacles[0]
    # obstacle.original_rect - прямоугольник препятствия
    # obstacle.center - центр прямоугольника препятсвия
    # obstacle.rotate_degree - угол на который нужно повернуть изначальный прямоугольник,
    # чтобы получился прямой
    # obstacle.normalized_rect - прямоугольник развернутый прямо
    # obstacle.size - размер прямоугольника
    # (равен river_generation.obstacles_generation.OBSTACLE_SIZE (5x5))
    return obstacles


if __name__ == '__main__':
    print(get_river_geometry())