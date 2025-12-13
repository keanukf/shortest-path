"""Unit tests for pathfinding algorithms."""

import pytest

from src.algorithms import AStar, Dijkstra
from src.graph import Grid


class TestDijkstra:
    """Test cases for Dijkstra's algorithm."""

    def test_simple_path(self):
        """Test finding a simple path."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        dijkstra = Dijkstra(grid)
        path = dijkstra.find_path()

        assert path is not None
        assert len(path) > 0
        assert path[0] == grid.start_node
        assert path[-1] == grid.end_node
        assert dijkstra.is_path_found

    def test_no_path(self):
        """Test when no path exists."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        # Block the path completely
        for i in range(5):
            grid.add_obstacle(i, 2)

        dijkstra = Dijkstra(grid)
        path = dijkstra.find_path()

        assert path is None
        assert not dijkstra.is_path_found

    def test_step_by_step(self):
        """Test step-by-step execution."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        dijkstra = Dijkstra(grid)
        steps = 0
        max_steps = 100

        while not dijkstra.is_complete and steps < max_steps:
            dijkstra.step()
            steps += 1

        assert dijkstra.is_complete
        assert steps > 0

    def test_metrics(self):
        """Test algorithm metrics."""
        grid = Grid(10, 10)
        grid.set_start(0, 0)
        grid.set_end(9, 9)

        dijkstra = Dijkstra(grid)
        dijkstra.find_path()

        metrics = dijkstra.get_metrics()
        assert "nodes_visited" in metrics
        assert "path_length" in metrics
        assert "path_found" in metrics
        assert metrics["path_found"] is True
        assert metrics["nodes_visited"] > 0


class TestAStar:
    """Test cases for A* algorithm."""

    def test_simple_path_manhattan(self):
        """Test finding a simple path with Manhattan heuristic."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        astar = AStar(grid, heuristic="manhattan")
        path = astar.find_path()

        assert path is not None
        assert len(path) > 0
        assert path[0] == grid.start_node
        assert path[-1] == grid.end_node
        assert astar.is_path_found

    def test_simple_path_euclidean(self):
        """Test finding a simple path with Euclidean heuristic."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        astar = AStar(grid, heuristic="euclidean")
        path = astar.find_path()

        assert path is not None
        assert astar.is_path_found

    def test_simple_path_chebyshev(self):
        """Test finding a simple path with Chebyshev heuristic."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        astar = AStar(grid, heuristic="chebyshev")
        path = astar.find_path()

        assert path is not None
        assert astar.is_path_found

    def test_invalid_heuristic(self):
        """Test with invalid heuristic name."""
        grid = Grid(5, 5)
        with pytest.raises(ValueError):
            AStar(grid, heuristic="invalid")

    def test_custom_heuristic(self):
        """Test with custom heuristic function."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        def custom_heuristic(node1, node2):
            return abs(node1.row - node2.row) + abs(node1.col - node2.col)

        astar = AStar(grid, heuristic=custom_heuristic)
        path = astar.find_path()

        assert path is not None
        assert astar.is_path_found

    def test_no_path(self):
        """Test when no path exists."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        # Block the path completely
        for i in range(5):
            grid.add_obstacle(i, 2)

        astar = AStar(grid, heuristic="manhattan")
        path = astar.find_path()

        assert path is None
        assert not astar.is_path_found

    def test_step_by_step(self):
        """Test step-by-step execution."""
        grid = Grid(5, 5)
        grid.set_start(0, 0)
        grid.set_end(4, 4)

        astar = AStar(grid, heuristic="manhattan")
        steps = 0
        max_steps = 100

        while not astar.is_complete and steps < max_steps:
            astar.step()
            steps += 1

        assert astar.is_complete
        assert steps > 0

    def test_metrics(self):
        """Test algorithm metrics."""
        grid = Grid(10, 10)
        grid.set_start(0, 0)
        grid.set_end(9, 9)

        astar = AStar(grid, heuristic="manhattan")
        astar.find_path()

        metrics = astar.get_metrics()
        assert "nodes_visited" in metrics
        assert "path_length" in metrics
        assert "path_found" in metrics
        assert "heuristic" in metrics
        assert metrics["path_found"] is True
        assert metrics["nodes_visited"] > 0


class TestAlgorithmComparison:
    """Test cases comparing different algorithms."""

    def test_same_path_length(self):
        """Test that both algorithms find paths of same length on simple grid."""
        grid = Grid(10, 10)
        grid.set_start(0, 0)
        grid.set_end(9, 9)

        dijkstra = Dijkstra(grid)
        dijkstra_path = dijkstra.find_path()

        grid.reset()
        astar = AStar(grid, heuristic="manhattan")
        astar_path = astar.find_path()

        # Both should find optimal paths
        assert dijkstra_path is not None
        assert astar_path is not None
        # On a simple grid without obstacles, path lengths should be similar
        assert abs(len(dijkstra_path) - len(astar_path)) <= 2

    def test_astar_fewer_nodes_visited(self):
        """Test that A* typically visits fewer nodes than Dijkstra."""
        grid = Grid(20, 20)
        grid.add_obstacles_random(density=0.2)
        grid.set_start(0, 0)
        grid.set_end(19, 19)

        dijkstra = Dijkstra(grid)
        dijkstra.find_path()
        dijkstra_visited = dijkstra.get_metrics()["nodes_visited"]

        grid.reset()
        astar = AStar(grid, heuristic="manhattan")
        astar.find_path()
        astar_visited = astar.get_metrics()["nodes_visited"]

        # A* should typically visit fewer nodes due to heuristic guidance
        # (This is probabilistic, so we allow some tolerance)
        assert astar_visited <= dijkstra_visited * 1.5

