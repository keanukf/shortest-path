"""Dijkstra's algorithm implementation for shortest path finding."""

import heapq
from typing import List, Optional

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import Node


class Dijkstra(PathfindingAlgorithm):
    """
    Dijkstra's algorithm for finding shortest paths.

    Dijkstra's algorithm is a graph search algorithm that solves the
    single-source shortest path problem for a graph with non-negative
    edge weights. It guarantees finding the optimal path.

    The algorithm works by:
    1. Starting at the source node with cost 0
    2. Exploring neighbors and updating their costs
    3. Always expanding the node with the minimum cost
    4. Continuing until the goal is reached or all reachable nodes are explored

    Time Complexity: O((V + E) log V) where V is vertices and E is edges
    Space Complexity: O(V)
    """

    def __init__(self, grid: Grid):
        """
        Initialize Dijkstra's algorithm.

        Args:
            grid: The grid on which to perform pathfinding.
        """
        super().__init__(grid)
        self.priority_queue: List[tuple[float, int, Node]] = []
        self.queue_counter = 0  # For tie-breaking in priority queue

    def reset(self) -> None:
        """Reset the algorithm to its initial state."""
        super().reset()
        self.priority_queue.clear()
        self.queue_counter = 0

    def initialize(self) -> None:
        """Initialize the algorithm for step-by-step execution."""
        super().initialize()
        if self.is_complete:
            return

        # Initialize priority queue with start node
        start = self.grid.start_node
        start.cost = 0.0
        heapq.heappush(self.priority_queue, (0.0, self.queue_counter, start))
        self.queue_counter += 1
        self._mark_frontier(start)

    def find_path(self) -> Optional[List[Node]]:
        """
        Find the shortest path from start to end using Dijkstra's algorithm.

        Returns:
            List of nodes forming the path, or None if no path exists.
        """
        self.reset()
        self.grid.reset()

        if not self.grid.start_node or not self.grid.end_node:
            self.is_complete = True
            return None

        # Initialize priority queue with start node
        start = self.grid.start_node
        start.cost = 0.0
        heapq.heappush(self.priority_queue, (0.0, self.queue_counter, start))
        self.queue_counter += 1
        self._mark_frontier(start)

        # Main algorithm loop
        while self.priority_queue:
            if not self.step():
                break

        self.is_complete = True
        return self.path

    def step(self) -> bool:
        """
        Execute one step of Dijkstra's algorithm.

        Returns:
            True if the algorithm should continue, False if it's complete.
        """
        if self.is_complete:
            return False

        if not self.priority_queue:
            # No more nodes to explore, path not found
            self.is_complete = True
            return False

        # Get node with minimum cost
        current_cost, _, current = heapq.heappop(self.priority_queue)

        # Skip if we've already found a better path to this node
        if current in self.visited_nodes:
            return True

        # Mark as visited
        self._mark_visited(current)

        # Check if we reached the goal
        if current == self.grid.end_node:
            self.path = self._reconstruct_path(current)
            self.is_path_found = True
            self.is_complete = True
            return False

        # Explore neighbors
        for neighbor, edge_cost in self.grid.get_neighbors(current):
            if neighbor in self.visited_nodes:
                continue

            # Calculate new cost
            new_cost = current.cost + edge_cost

            # If we found a better path, update it
            if new_cost < neighbor.cost:
                neighbor.cost = new_cost
                neighbor.parent = current
                heapq.heappush(
                    self.priority_queue, (new_cost, self.queue_counter, neighbor)
                )
                self.queue_counter += 1
                self._mark_frontier(neighbor)

        return True

