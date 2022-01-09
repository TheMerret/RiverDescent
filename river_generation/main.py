from river_generation.river_generation import RiverGeneration


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


if __name__ == '__main__':
    print(get_river_geometry())