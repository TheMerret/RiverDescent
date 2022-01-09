import timeit
from river_generation.river_generation import RiverGeneration, ClosingSegmentNotFound
from river_generation.temp.river_generation_test import viz_river_generation
from river_generation.utils import offset_polyline


def test_river_path_generation():
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


def test_offsetting_performance():
    test_polyline = [(553.7137223974763, 64.40496845425868), (587.873246492986, 64.11548096192385),
                     (510.1274787535411, 196.28328611898016),
                     (515.7948066610218, 205.83234546994072),
                     (480.9682926829268, 300.8137472283814), (464.0598548972189, 307.5386940749698),
                     (452.2993931220499, 313.4865138233311), (428.81779067440465, 354.4725835501301),
                     (428.1423974255833, 358.31938857602574),
                     (373.6608738828203, 393.45233366434957),
                     (359.9140127388535, 397.52547770700636),
                     (325.92243975903614, 431.83772590361446),
                     (326.9146341463415, 434.979674796748), (293.05737704918033, 559.1229508196722),
                     (286.42814371257487, 566.5808383233533), (314.6855072463768, 633.1033816425121),
                     (293.5143947655398, 735.430425299891), (294.07797427652736, 736.5176848874598),
                     (145.9178544636159, 806.5570142535634), (137.80255839822024, 817.6779755283649),
                     (113.0820170109356, 828.0370595382747), (99.52080257683532, 841.8963226412562),
                     (61.98032520325203, 856.7978861788617), (68.42957746478874, 923.0492957746479),
                     (11.0, 945.5217391304348), (10.999999999999986, 970.4772727272726),
                     (51.38888888888906, 987.0)]
    num_runs = 100
    funcs = [lambda: RiverGeneration.get_expanded_river_exterior_from_path(test_polyline, 20),
             lambda: offset_polyline(test_polyline, 20)]
    for ind, func in enumerate(funcs):
        duration = timeit.Timer(func).timeit(number=num_runs)
        avg_duration = duration / num_runs
        print(f'{ind}: {".".join(func.__code__.co_names)}. On average it took {avg_duration} seconds,'
              f' all duration - {duration},'
              f' number of runs - {num_runs}')


def test_close_segments_search():
    while True:
        rg = RiverGeneration(1000, 100)
        river_path = rg.get_river_path()
        try:
            river_exterior = rg.get_expanded_river_exterior_from_path2(river_path, 20)
        except AttributeError:
            print(river_path)
            return
        try:
            rg.get_river_geom_from_path_and_exterior(river_path, river_exterior)
        except (ClosingSegmentNotFound, ):
            print(river_path)
            return


def main():
    test_close_segments_search()


if __name__ == '__main__':
    main()
