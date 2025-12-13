"""Grid-based graph representation for pathfinding algorithms."""

import random
from typing import List, Optional, Tuple

from src.graph.node import Node, NodeState


class Grid:
    """
    A 2D grid-based graph for pathfinding algorithms.

    The grid represents a graph where each cell is a node, and nodes are
    connected to their neighbors (orthogonal and optionally diagonal).

    Attributes:
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        allow_diagonal: Whether diagonal movement is allowed.
        nodes: 2D array of Node objects.
        start_node: Starting node for pathfinding.
        end_node: Goal node for pathfinding.
    """

    def __init__(
        self,
        width: int,
        height: int,
        allow_diagonal: bool = False,
        diagonal_cost: float = 1.414,
    ):
        """
        Initialize a grid.

        Args:
            width: Number of columns in the grid.
            height: Number of rows in the grid.
            allow_diagonal: Whether diagonal movement is allowed.
            diagonal_cost: Cost of diagonal movement (default: sqrt(2) ≈ 1.414).
        """
        if width <= 0 or height <= 0:
            raise ValueError("Grid dimensions must be positive")

        self.width = width
        self.height = height
        self.allow_diagonal = allow_diagonal
        self.diagonal_cost = diagonal_cost

        # Create 2D array of nodes
        self.nodes: List[List[Node]] = [
            [Node(row, col) for col in range(width)] for row in range(height)
        ]

        self.start_node: Optional[Node] = None
        self.end_node: Optional[Node] = None

    def get_node(self, row: int, col: int) -> Optional[Node]:
        """
        Get a node at the specified position.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            Node at the position, or None if out of bounds.
        """
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.nodes[row][col]
        return None

    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Check if a position is within grid bounds.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if the position is valid.
        """
        return 0 <= row < self.height and 0 <= col < self.width

    def get_neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """
        Get all valid neighbors of a node with their movement costs.

        Args:
            node: The node to get neighbors for.

        Returns:
            List of tuples (neighbor_node, movement_cost).
        """
        neighbors: List[Tuple[Node, float]] = []
        row, col = node.row, node.col

        # Orthogonal neighbors (up, down, left, right)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            neighbor = self.get_node(new_row, new_col)
            if neighbor and neighbor.is_traversable():
                neighbors.append((neighbor, 1.0))

        # Diagonal neighbors (if allowed)
        if self.allow_diagonal:
            diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in diagonal_directions:
                new_row, new_col = row + dr, col + dc
                neighbor = self.get_node(new_row, new_col)
                if neighbor and neighbor.is_traversable():
                    neighbors.append((neighbor, self.diagonal_cost))

        return neighbors

    def set_start(self, row: int, col: int) -> bool:
        """
        Set the start position for pathfinding.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if the start position was set successfully.
        """
        node = self.get_node(row, col)
        if node and node.is_traversable():
            if self.start_node:
                self.start_node.state = NodeState.UNVISITED
            self.start_node = node
            node.state = NodeState.START
            node.cost = 0.0
            node.g_cost = 0.0
            return True
        return False

    def set_end(self, row: int, col: int) -> bool:
        """
        Set the end (goal) position for pathfinding.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if the end position was set successfully.
        """
        node = self.get_node(row, col)
        if node and node.is_traversable():
            if self.end_node:
                self.end_node.state = NodeState.UNVISITED
            self.end_node = node
            node.state = NodeState.END
            return True
        return False

    def add_obstacle(self, row: int, col: int) -> bool:
        """
        Add an obstacle at the specified position.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if the obstacle was added successfully.
        """
        node = self.get_node(row, col)
        if node:
            node.set_obstacle(True)
            return True
        return False

    def remove_obstacle(self, row: int, col: int) -> bool:
        """
        Remove an obstacle at the specified position.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if the obstacle was removed successfully.
        """
        node = self.get_node(row, col)
        if node:
            node.set_obstacle(False)
            return True
        return False

    def add_obstacles_random(self, density: float = 0.3) -> None:
        """
        Randomly place obstacles in the grid.

        Args:
            density: Fraction of cells to fill with obstacles (0.0 to 1.0).
        """
        if not 0.0 <= density <= 1.0:
            raise ValueError("Density must be between 0.0 and 1.0")

        total_cells = self.width * self.height
        num_obstacles = int(total_cells * density)

        # Exclude start and end positions from obstacle placement
        excluded_positions = set()
        if self.start_node:
            excluded_positions.add((self.start_node.row, self.start_node.col))
        if self.end_node:
            excluded_positions.add((self.end_node.row, self.end_node.col))

        available_positions = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (r, c) not in excluded_positions
        ]

        random.shuffle(available_positions)
        for i in range(min(num_obstacles, len(available_positions))):
            row, col = available_positions[i]
            self.add_obstacle(row, col)

    def clear_obstacles(self) -> None:
        """Remove all obstacles from the grid."""
        for row in self.nodes:
            for node in row:
                if node.state == NodeState.OBSTACLE:
                    node.set_obstacle(False)

    def reset(self) -> None:
        """Reset all nodes to their initial state (preserves obstacles and start/end)."""
        start_pos = (self.start_node.row, self.start_node.col) if self.start_node else None
        end_pos = (self.end_node.row, self.end_node.col) if self.end_node else None

        for row in self.nodes:
            for node in row:
                node.reset()

        if start_pos:
            self.set_start(start_pos[0], start_pos[1])
        if end_pos:
            self.set_end(end_pos[0], end_pos[1])

    def get_path(self) -> Optional[List[Node]]:
        """
        Reconstruct the path from start to end.

        Returns:
            List of nodes forming the path, or None if no path exists.
        """
        if not self.end_node or not self.end_node.parent:
            return None

        path: List[Node] = []
        current = self.end_node

        while current:
            path.append(current)
            current = current.parent

        path.reverse()
        return path

    def __repr__(self) -> str:
        """String representation of the grid."""
        return f"Grid({self.width}x{self.height}, diagonal={self.allow_diagonal})"

