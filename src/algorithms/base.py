"""Abstract base class for pathfinding algorithms."""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from src.graph.grid import Grid
from src.graph.node import Node, NodeState


class PathfindingAlgorithm(ABC):
    """
    Abstract base class for pathfinding algorithms.

    This class defines the interface that all pathfinding algorithms must
    implement, enabling step-by-step execution for visualization purposes.

    Attributes:
        grid: The grid on which to perform pathfinding.
        visited_nodes: Set of nodes that have been visited.
        path: The final path from start to end (if found).
        is_complete: Whether the algorithm has finished execution.
        is_path_found: Whether a path was found.
    """

    def __init__(self, grid: Grid):
        """
        Initialize the pathfinding algorithm.

        Args:
            grid: The grid on which to perform pathfinding.
        """
        self.grid = grid
        self.visited_nodes: set[Node] = set()
        self.path: Optional[List[Node]] = None
        self.is_complete = False
        self.is_path_found = False

        # Callbacks for visualization
        self.on_node_visited: Optional[Callable[[Node], None]] = None
        self.on_node_explored: Optional[Callable[[Node], None]] = None
        self.on_path_found: Optional[Callable[[List[Node]], None]] = None

    def reset(self) -> None:
        """Reset the algorithm to its initial state."""
        self.grid.reset()
        self.visited_nodes.clear()
        self.path = None
        self.is_complete = False
        self.is_path_found = False

    @abstractmethod
    def find_path(self) -> Optional[List[Node]]:
        """
        Find the shortest path from start to end.

        This method runs the algorithm to completion.

        Returns:
            List of nodes forming the path, or None if no path exists.
        """
        pass

    def initialize(self) -> None:
        """
        Initialize the algorithm for step-by-step execution.
        
        This method sets up the algorithm's initial state (e.g., adding
        the start node to the priority queue) so that step() can be called.
        Should be called after reset() and before calling step().
        """
        if not self.grid.start_node or not self.grid.end_node:
            self.is_complete = True
            return

    @abstractmethod
    def step(self) -> bool:
        """
        Execute one step of the algorithm.

        This method allows incremental execution for visualization purposes.

        Returns:
            True if the algorithm should continue, False if it's complete.
        """
        pass

    def _mark_visited(self, node: Node) -> None:
        """
        Mark a node as visited and trigger callbacks.

        Args:
            node: The node to mark as visited.
        """
        if node.state not in (NodeState.START, NodeState.END, NodeState.OBSTACLE):
            node.state = NodeState.VISITED
        self.visited_nodes.add(node)

        if self.on_node_visited:
            self.on_node_visited(node)

    def _mark_frontier(self, node: Node) -> None:
        """
        Mark a node as being in the frontier.

        Args:
            node: The node to mark as frontier.
        """
        if node.state not in (NodeState.START, NodeState.END, NodeState.OBSTACLE):
            node.state = NodeState.FRONTIER

        if self.on_node_explored:
            self.on_node_explored(node)

    def _reconstruct_path(self, end_node: Node) -> List[Node]:
        """
        Reconstruct the path from start to end using parent pointers.

        Args:
            end_node: The end node.

        Returns:
            List of nodes forming the path.
        """
        path: List[Node] = []
        current: Optional[Node] = end_node

        while current:
            path.append(current)
            current = current.parent

        path.reverse()

        # Mark path nodes
        for node in path:
            if node.state not in (NodeState.START, NodeState.END):
                node.state = NodeState.PATH

        if self.on_path_found:
            self.on_path_found(path)

        return path

    def get_metrics(self) -> dict:
        """
        Get performance metrics for the algorithm execution.

        Returns:
            Dictionary containing metrics like nodes_visited, path_length, etc.
        """
        path_length = len(self.path) if self.path else 0
        return {
            "nodes_visited": len(self.visited_nodes),
            "path_length": path_length,
            "path_found": self.is_path_found,
            "algorithm": self.__class__.__name__,
        }

