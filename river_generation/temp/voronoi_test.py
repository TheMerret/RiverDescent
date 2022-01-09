from itertools import groupby
from typing import List
from foronoi import Voronoi, Polygon, Visualizer, Point, VoronoiObserver
from foronoi.graph import HalfEdge, Vertex

# Define some points (a.k.a sites or cell points)
points = [
    (2.5, 2.5), (4, 7.5), (7.5, 2.5), (6, 7.5), (4, 4), (3, 3), (6, 3)
]

# Define a bounding box / polygon
polygon = Polygon([
    (2.5, 10), (5, 10), (10, 5), (10, 2.5), (5, 0), (2.5, 0), (0, 2.5), (0, 5)
])

# Initialize the algorithm
v = Voronoi(polygon)

# Optional: visualize the voronoi diagram at every step.
# You can find more information in the observers.py example file
# v.attach_observer(
#     VoronoiObserver()
# )

# Create the Voronoi diagram
v.create_diagram(points=points)

# Visualize the Voronoi diagram
# Visualizer(v) \
#     .plot_sites(show_labels=False) \
#     .plot_edges(show_labels=False) \
#     .plot_vertices() \
#     .show()

# Some examples of how to access properties from the Voronoi diagram:
edges: List[HalfEdge] = v.edges  # A list of all edges
vertices: List[Vertex] = v.vertices  # A list of all vertices
sites: List[Point] = v.sites  # A list of all cell points (a.k.a. sites)

edge, vertex, site = edges[0], vertices[0], sites[0]

# Edge operations
origin: Vertex = edge.origin  # The vertex in which the edge originates
target: Vertex = edge.twin.origin  # The twin is the edge that goes in the other direction
target_alt: Vertex = edge.target  # Same as above, but more convenient
twin: HalfEdge = edge.twin  # Get the twin of this edge
next_edge: HalfEdge = edge.next  # Get the next edge
prev_edge: HalfEdge = edge.twin.next  # Get the previous edge
prev_alt: HalfEdge = edge.prev  # Same as above, but more convenient

# Site operations
size: float = site.area()  # The area of the cell
borders: List[HalfEdge] = site.borders()  # A list of all the borders that surround this cell point
vertices: List[Vertex] = site.vertices()  # A list of all the vertices around this cell point
site_x: float = site.x  # X-coordinate of the site
site_xy: [float, float] = site.xy  # (x, y)-coordinates of the site
first_edge: HalfEdge = site.first_edge  # Points to the first edge that is part of the border around the site

# Vertex operations
connected_edges: List[
    HalfEdge] = vertex.connected_edges  # A list of all edges that are connected to this vertex
vertex_x: float = vertex.x  # x-coordinate of the vertex
vertex_xy: [float, float] = vertex.xy  # (x, y)-coordinates of the vertex


def line_eq_from_points(p1, p2):
    a = p2[1] - p1[1]
    b = p1[0] - p2[0]
    c = a * p1[0] + b * p1[1]
    return a, b, c


def is_point_on_line(p, a, b, c):
    x, y = p
    return a * x + b * y == c


# def is_point_lie_on_between_points(p, pts):
#     lines = ((pts[i - 1], pts[i]) for i in range(len(pts)))
#     line_eqs = (line_eq_from_points(p1.xy, p2.xy) for p1, p2 in lines)



min_poly_vertices = list(next(groupby(sorted(polygon.points, key=lambda p: p.y),
                                      key=lambda x: x.y))[1])
poly_lines = [(min_poly_vertices[i - 1], min_poly_vertices[i])
              for i in range(1, len(min_poly_vertices))]
poly_lines = [line_eq_from_points(p1.xy, p2.xy) for p1, p2 in poly_lines]
v_points = {j for i in edges for j in (i.origin, i.twin.origin)}
edge_sites = set()
min_vertices = set()


for i in v_points:
    vert_sites = set()
    if any(is_point_on_line(i.xy, a, b, c) for a, b, c in poly_lines):
        min_vertices.add(i)
        for he in i.connected_edges:
            s = he.incident_point
            if isinstance(s, Point):
                vert_sites.add(s)
    edge_sites.update(vert_sites)

# print(*(i.xy for i in edge_sites))
extended_min_vertices = {j for i in min_vertices for j in i.connected_edges}
res_edges = set()
poly_lines = ((polygon.points[i - 1], polygon.points[i])
              for i in range(1, len(polygon.points)))
poly_lines = [line_eq_from_points(p1.xy, p2.xy) for p1, p2 in poly_lines]
for v in extended_min_vertices:
    if (not any(is_point_on_line(v.target.xy, a, b, c) for a, b, c in poly_lines)
            or not any(is_point_on_line(v.origin.xy, a, b, c) for a, b, c in poly_lines)):
        res_edges.add(v)

print(*(j.xy for i in res_edges for j in (i.origin, i.target)))