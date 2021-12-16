from main import RiverGeneration
from river_generation import viz_river_generation


def main():
    while True:
        rg = RiverGeneration(1000, 100)
        start_edges = rg.get_start_edges()
        end_points = rg.get_end_points()
        start, end = rg.get_start_and_end_from_variants((start_edges, end_points))
        try:
            rg.get_path_from_start_and_end(start, end)
        except KeyError:
            print([i.xy for i in rg.voronoi.sites])
            print([i.xy for i in rg.voronoi.bounding_poly.points])
            print('start', start.xy, 'end', end.xy)
            viz_river_generation(rg.voronoi, start_edges, end_points)


if __name__ == '__main__':
    main()