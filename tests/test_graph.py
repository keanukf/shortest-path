"""Unit tests for graph data structures."""

import pytest

from src.graph.grid import Grid
from src.graph.node import Node, NodeState


class TestNode:
    """Test cases for Node class."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = Node(5, 10)
        assert node.row == 5
        assert node.col == 10
        assert node.state == NodeState.UNVISITED
        assert node.cost == float("inf")

    def test_node_obstacle(self):
        """Test obstacle node creation."""
        node = Node(0, 0, is_obstacle=True)
        assert node.state == NodeState.OBSTACLE
        assert not node.is_traversable()

    def test_node_equality(self):
        """Test node equality based on position."""
        node1 = Node(5, 10)
        node2 = Node(5, 10)
        node3 = Node(5, 11)

        assert node1 == node2
        assert node1 != node3

    def test_node_reset(self):
        """Test node reset functionality."""
        node = Node(0, 0)
        node.cost = 5.0
        node.state = NodeState.VISITED
        node.parent = Node(1, 1)

        node.reset()
        assert node.cost == float("inf")
        assert node.state == NodeState.UNVISITED
        assert node.parent is None

    def test_node_obstacle_toggle(self):
        """Test toggling obstacle status."""
        node = Node(0, 0)
        assert node.is_traversable()

        node.set_obstacle(True)
        assert not node.is_traversable()
        assert node.state == NodeState.OBSTACLE

        node.set_obstacle(False)
        assert node.is_traversable()
        assert node.state == NodeState.UNVISITED


class TestGrid:
    """Test cases for Grid class."""

    def test_grid_creation(self):
        """Test basic grid creation."""
        grid = Grid(10, 20)
        assert grid.width == 10
        assert grid.height == 20
        assert len(grid.nodes) == 20
        assert len(grid.nodes[0]) == 10

    def test_grid_invalid_dimensions(self):
        """Test grid creation with invalid dimensions."""
        with pytest.raises(ValueError):
            Grid(0, 10)
        with pytest.raises(ValueError):
            Grid(10, -5)

    def test_get_node(self):
        """Test getting nodes from grid."""
        grid = Grid(10, 10)
        node = grid.get_node(5, 5)
        assert node is not None
        assert node.row == 5
        assert node.col == 5

        # Out of bounds
        assert grid.get_node(15, 5) is None
        assert grid.get_node(5, 15) is None

    def test_set_start_end(self):
        """Test setting start and end positions."""
        grid = Grid(10, 10)
        assert grid.set_start(0, 0)
        assert grid.start_node is not None
        assert grid.start_node.row == 0
        assert grid.start_node.col == 0
        assert grid.start_node.state == NodeState.START

        assert grid.set_end(9, 9)
        assert grid.end_node is not None
        assert grid.end_node.row == 9
        assert grid.end_node.col == 9
        assert grid.end_node.state == NodeState.END

    def test_add_obstacle(self):
        """Test adding obstacles."""
        grid = Grid(10, 10)
        assert grid.add_obstacle(5, 5)
        node = grid.get_node(5, 5)
        assert node.state == NodeState.OBSTACLE

    def test_get_neighbors_orthogonal(self):
        """Test getting orthogonal neighbors."""
        grid = Grid(10, 10)
        node = grid.get_node(5, 5)
        neighbors = grid.get_neighbors(node)

        # Should have up to 4 orthogonal neighbors
        assert len(neighbors) <= 4
        neighbor_positions = {(n.row, n.col) for n, _ in neighbors}
        assert (4, 5) in neighbor_positions or (6, 5) in neighbor_positions
        assert (5, 4) in neighbor_positions or (5, 6) in neighbor_positions

    def test_get_neighbors_diagonal(self):
        """Test getting neighbors with diagonal movement."""
        grid = Grid(10, 10, allow_diagonal=True)
        node = grid.get_node(5, 5)
        neighbors = grid.get_neighbors(node)

        # Should have up to 8 neighbors (4 orthogonal + 4 diagonal)
        assert len(neighbors) <= 8

    def test_obstacle_blocking(self):
        """Test that obstacles block neighbor access."""
        grid = Grid(10, 10)
        grid.add_obstacle(4, 5)
        grid.add_obstacle(6, 5)

        node = grid.get_node(5, 5)
        neighbors = grid.get_neighbors(node)

        # Should not include obstacle neighbors
        neighbor_positions = {(n.row, n.col) for n, _ in neighbors}
        assert (4, 5) not in neighbor_positions
        assert (6, 5) not in neighbor_positions

    def test_random_obstacles(self):
        """Test random obstacle placement."""
        grid = Grid(20, 20)
        grid.set_start(0, 0)
        grid.set_end(19, 19)
        grid.add_obstacles_random(density=0.3)

        obstacle_count = sum(
            1
            for row in grid.nodes
            for node in row
            if node.state == NodeState.OBSTACLE
        )
        # Should have approximately 30% obstacles (excluding start/end)
        total_cells = 20 * 20 - 2
        expected_min = int(total_cells * 0.25)
        expected_max = int(total_cells * 0.35)
        assert expected_min <= obstacle_count <= expected_max

    def test_path_reconstruction(self):
        """Test path reconstruction."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        # Manually create a path
        nodes = [grid.get_node(i, i) for i in range(5)]
        for i in range(1, len(nodes)):
            nodes[i].parent = nodes[i - 1]

        path = grid.get_path()
        assert path is not None
        assert len(path) == 5
        assert path[0] == grid.start_node
        assert path[-1] == grid.end_node

    def test_reset(self):
        """Test grid reset functionality."""
        grid = Grid(10, 10)
        grid.set_start(0, 0)
        grid.set_end(9, 9)
        grid.add_obstacle(5, 5)

        # Modify some nodes
        node = grid.get_node(3, 3)
        node.cost = 5.0
        node.state = NodeState.VISITED

        grid.reset()

        # Start and end should be preserved
        assert grid.start_node is not None
        assert grid.end_node is not None
        # Obstacle should be preserved
        assert grid.get_node(5, 5).state == NodeState.OBSTACLE
        # Modified node should be reset
        assert grid.get_node(3, 3).cost == float("inf")

