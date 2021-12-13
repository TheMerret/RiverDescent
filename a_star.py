from typing import List, Dict

import foronoi
from foronoi import Voronoi, Polygon, Visualizer, Point, VoronoiObserver
from foronoi.visualization.visualizer import Colors
from foronoi.graph import HalfEdge, Vertex


class Graph:

    def __init__(self, edges: Dict[Vertex, List[Vertex]]):

        self.vertex_edges = edges
        self.edges = {k.xy: [i.xy for i in v] for k, v in self.vertex_edges.items()}

    def neighbours(self, location: Vertex) -> List[Vertex]:
        return self.edges[location]


frontier = PriorityQueue()
frontier.put(start, 0)
came_from = dict()
cost_from_start = dict()
came_from[start] = None
cost_from_start[start] = 0


def heuristic(a, b):
    # Manhattan distance on a square grid
    return abs(a.x - b.x) + abs(a.y - b.y)


while not frontier.empty():
    current = frontier.get()

    if current == goal:
        break

    for next in graph.neighbors(current):
        new_cost = cost_from_start[current] + graph.cost(current, next)
        if next not in cost_from_start or new_cost < cost_from_start[next]:
            cost_from_start[next] = new_cost
            priority = new_cost + heuristic(goal, next)
            frontier.put(next, priority)
            came_from[next] = current

current = goal
path = []
while current != start:
    path.append(current)
    current = came_from[current]
path.append(start)
path.reverse()
