from typing import Dict, List, Set
import heapq


class Graph:
    def __init__(self):
        self.nodes = {}  # Dictionary to store nodes and their connections

    def add_node(self, node: str):
        """Add a new node to the graph if it doesn't exist."""
        if node not in self.nodes:
            self.nodes[node] = {}

    def add_edge(self, from_node: str, to_node: str, weight: float):
        """Add a weighted edge between two nodes."""
        self.add_node(from_node)
        self.add_node(to_node)
        self.nodes[from_node][to_node] = weight

    def dijkstra(self, start: str) -> tuple[Dict[str, float], Dict[str, str]]:
        """
        Implement Dijkstra's algorithm to find shortest paths from start node.
        Returns a tuple of (distances, predecessors).
        """
        distances = {node: float('infinity') for node in self.nodes}
        predecessors = {node: None for node in self.nodes}
        distances[start] = 0
        pq = [(0, start)]
        visited = set()

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            for neighbor, weight in self.nodes[current_node].items():
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        return distances, predecessors

    def get_shortest_path(self, start: str, end: str) -> tuple[List[str], float]:
        """
        Get the shortest path between start and end nodes.
        Returns a tuple of (path, total_distance).
        """
        distances, predecessors = self.dijkstra(start)

        if distances[end] == float('infinity'):
            return [], float('infinity')

        path = []
        current_node = end

        while current_node is not None:
            path.append(current_node)
            current_node = predecessors[current_node]

        path.reverse()
        return path, distances[end]
