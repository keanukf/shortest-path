"""Node class for representing grid cells in pathfinding algorithms."""

from enum import Enum
from typing import Optional


class NodeState(Enum):
    """State of a node during pathfinding."""

    UNVISITED = "unvisited"
    VISITED = "visited"
    FRONTIER = "frontier"
    PATH = "path"
    OBSTACLE = "obstacle"
    START = "start"
    END = "end"


class Node:
    """
    Represents a single node (cell) in a grid-based graph.

    Each node tracks its position, state, cost, and parent for path reconstruction.

    Attributes:
        row: Row index in the grid.
        col: Column index in the grid.
        state: Current state of the node (unvisited, visited, etc.).
        cost: Cost to reach this node from the start.
        parent: Parent node for path reconstruction.
        g_cost: Actual cost from start to this node (for A*).
        h_cost: Heuristic cost from this node to goal (for A*).
        f_cost: Total estimated cost (g + h) for A*.
    """

    def __init__(self, row: int, col: int, is_obstacle: bool = False):
        """
        Initialize a node.

        Args:
            row: Row index in the grid.
            col: Column index in the grid.
            is_obstacle: Whether this node is an obstacle.
        """
        self.row = row
        self.col = col
        self.state = NodeState.OBSTACLE if is_obstacle else NodeState.UNVISITED
        self.cost = float("inf")
        self.parent: Optional["Node"] = None

        # A* specific attributes
        self.g_cost = float("inf")  # Actual cost from start
        self.h_cost = 0.0  # Heuristic cost to goal
        self.f_cost = float("inf")  # Total estimated cost (g + h)

    def __eq__(self, other: object) -> bool:
        """Check if two nodes are equal based on position."""
        if not isinstance(other, Node):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        """Hash based on position."""
        return hash((self.row, self.col))

    def __lt__(self, other: "Node") -> bool:
        """Compare nodes for priority queue ordering."""
        if self.f_cost != other.f_cost:
            return self.f_cost < other.f_cost
        return self.cost < other.cost

    def __repr__(self) -> str:
        """String representation of the node."""
        return f"Node({self.row}, {self.col}, state={self.state.value})"

    def reset(self) -> None:
        """Reset node to initial state (except obstacle status)."""
        if self.state != NodeState.OBSTACLE:
            self.state = NodeState.UNVISITED
        self.cost = float("inf")
        self.parent = None
        self.g_cost = float("inf")
        self.h_cost = 0.0
        self.f_cost = float("inf")

    def set_obstacle(self, is_obstacle: bool) -> None:
        """
        Set or remove obstacle status.

        Args:
            is_obstacle: True to make this an obstacle, False to remove obstacle.
        """
        if is_obstacle:
            self.state = NodeState.OBSTACLE
            self.cost = float("inf")
        elif self.state == NodeState.OBSTACLE:
            self.state = NodeState.UNVISITED
            self.cost = float("inf")

    def is_traversable(self) -> bool:
        """
        Check if the node can be traversed.

        Returns:
            True if the node is not an obstacle.
        """
        return self.state != NodeState.OBSTACLE

