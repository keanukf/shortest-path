"""A* algorithm implementation for shortest path finding."""

import heapq
from typing import Callable, List, Optional

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import Node
from src.utils.heuristics import get_heuristic, manhattan_distance


class AStar(PathfindingAlgorithm):
    """
    A* algorithm for finding shortest paths.

    A* is an informed search algorithm that uses both the actual cost from
    the start (g(n)) and a heuristic estimate to the goal (h(n)) to guide
    the search. It's optimal when using an admissible heuristic.

    The algorithm evaluates nodes using: f(n) = g(n) + h(n)
    where:
    - g(n): actual cost from start to node n
    - h(n): heuristic estimate from node n to goal
    - f(n): total estimated cost

    Time Complexity: O((V + E) log V) where V is vertices and E is edges
    Space Complexity: O(V)
    """

    def __init__(
        self,
        grid: Grid,
        heuristic: str | Callable[[Node, Node], float] = "manhattan",
    ):
        """
        Initialize A* algorithm.

        Args:
            grid: The grid on which to perform pathfinding.
            heuristic: Heuristic function name ("manhattan", "euclidean", "chebyshev")
                      or a custom heuristic function.
        """
        super().__init__(grid)

        # Set up heuristic function
        if isinstance(heuristic, str):
            self.heuristic_func = get_heuristic(heuristic)
            self.heuristic_name = heuristic
        else:
            self.heuristic_func = heuristic
            self.heuristic_name = "custom"

        self.priority_queue: List[tuple[float, float, int, Node]] = []
        self.queue_counter = 0  # For tie-breaking in priority queue

    def reset(self) -> None:
        """Reset the algorithm to its initial state."""
        super().reset()
        self.priority_queue.clear()
        self.queue_counter = 0

    def _calculate_heuristic(self, node: Node) -> float:
        """
        Calculate heuristic value for a node.

        Args:
            node: The node to calculate heuristic for.

        Returns:
            Heuristic estimate from node to goal.
        """
        if not self.grid.end_node:
            return 0.0
        return self.heuristic_func(node, self.grid.end_node)

    def find_path(self) -> Optional[List[Node]]:
        """
        Find the shortest path from start to end using A* algorithm.

        Returns:
            List of nodes forming the path, or None if no path exists.
        """
        self.reset()
        self.grid.reset()

        if not self.grid.start_node or not self.grid.end_node:
            self.is_complete = True
            return None

        # Initialize start node
        start = self.grid.start_node
        start.g_cost = 0.0
        start.h_cost = self._calculate_heuristic(start)
        start.f_cost = start.g_cost + start.h_cost
        start.cost = start.f_cost  # For compatibility

        # Add to priority queue: (f_cost, g_cost, counter, node)
        heapq.heappush(
            self.priority_queue, (start.f_cost, start.g_cost, self.queue_counter, start)
        )
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
        Execute one step of A* algorithm.

        Returns:
            True if the algorithm should continue, False if it's complete.
        """
        if self.is_complete:
            return False

        if not self.priority_queue:
            # No more nodes to explore, path not found
            self.is_complete = True
            return False

        # Get node with minimum f_cost
        _, _, _, current = heapq.heappop(self.priority_queue)

        # Skip if we've already visited this node with a better path
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

            # Calculate new g_cost
            new_g_cost = current.g_cost + edge_cost

            # Check if we found a better path to this neighbor
            if new_g_cost < neighbor.g_cost:
                neighbor.g_cost = new_g_cost
                neighbor.h_cost = self._calculate_heuristic(neighbor)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.cost = neighbor.f_cost  # For compatibility
                neighbor.parent = current

                # Add to priority queue
                heapq.heappush(
                    self.priority_queue,
                    (neighbor.f_cost, neighbor.g_cost, self.queue_counter, neighbor),
                )
                self.queue_counter += 1
                self._mark_frontier(neighbor)

        return True

    def get_metrics(self) -> dict:
        """
        Get performance metrics for the algorithm execution.

        Returns:
            Dictionary containing metrics including heuristic information.
        """
        metrics = super().get_metrics()
        metrics["heuristic"] = self.heuristic_name
        return metrics

