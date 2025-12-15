"""Performance metrics and analysis utilities for pathfinding algorithms."""

import time
from typing import Any, Dict, List

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import NodeState


class AlgorithmMetrics:
    """
    Container for algorithm performance metrics.

    Tracks execution time, nodes explored, path characteristics, and
    other relevant metrics for research and analysis purposes.
    """

    def __init__(self, algorithm_name: str):
        """
        Initialize metrics container.

        Args:
            algorithm_name: Name of the algorithm being measured.
        """
        self.algorithm_name = algorithm_name
        self.execution_time: float = 0.0
        self.nodes_visited: int = 0
        self.nodes_explored: int = 0  # Total nodes in frontier
        self.path_length: int = 0
        self.path_cost: float = 0.0
        self.path_found: bool = False
        self.memory_usage: int = 0  # Approximate memory usage
        self.additional_info: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary format.

        Returns:
            Dictionary containing all metrics.
        """
        return {
            "algorithm": self.algorithm_name,
            "execution_time": self.execution_time,
            "nodes_visited": self.nodes_visited,
            "nodes_explored": self.nodes_explored,
            "path_length": self.path_length,
            "path_cost": self.path_cost,
            "path_found": self.path_found,
            "memory_usage": self.memory_usage,
            **self.additional_info,
        }

    def __repr__(self) -> str:
        """String representation of metrics."""
        return (
            f"AlgorithmMetrics({self.algorithm_name}: "
            f"time={self.execution_time:.4f}s, "
            f"visited={self.nodes_visited}, "
            f"path_length={self.path_length})"
        )


def measure_algorithm(
    algorithm: PathfindingAlgorithm, include_step_by_step: bool = False
) -> AlgorithmMetrics:
    """
    Measure performance metrics for an algorithm execution.

    Args:
        algorithm: The pathfinding algorithm to measure.
        include_step_by_step: If True, measure step-by-step execution.

    Returns:
        AlgorithmMetrics object containing all measured metrics.
    """
    metrics = AlgorithmMetrics(algorithm.__class__.__name__)

    # Reset algorithm state
    algorithm.reset()
    algorithm.grid.reset()

    # Measure execution time
    start_time = time.perf_counter()

    if include_step_by_step:
        # Step-by-step execution for visualization
        while not algorithm.is_complete:
            algorithm.step()
    else:
        # Full execution
        algorithm.find_path()

    end_time = time.perf_counter()
    metrics.execution_time = end_time - start_time

    # Collect metrics from algorithm
    algo_metrics = algorithm.get_metrics()
    metrics.nodes_visited = algo_metrics.get("nodes_visited", 0)
    metrics.path_length = algo_metrics.get("path_length", 0)
    metrics.path_found = algo_metrics.get("path_found", False)

    # Calculate path cost
    if algorithm.path:
        metrics.path_cost = sum(
            algorithm.grid.get_neighbors(algorithm.path[i])[0][1]
            for i in range(len(algorithm.path) - 1)
            if algorithm.grid.get_neighbors(algorithm.path[i])
        )
        # More accurate path cost calculation
        total_cost = 0.0
        for i in range(len(algorithm.path) - 1):
            current = algorithm.path[i]
            next_node = algorithm.path[i + 1]
            neighbors = algorithm.grid.get_neighbors(current)
            for neighbor, cost in neighbors:
                if neighbor == next_node:
                    total_cost += cost
                    break
        metrics.path_cost = total_cost

    # Store additional algorithm-specific info
    for key, value in algo_metrics.items():
        if key not in ["nodes_visited", "path_length", "path_found", "algorithm"]:
            metrics.additional_info[key] = value

    return metrics


def clone_grid(grid: Grid) -> Grid:
    """
    Create a deep copy of a grid with all obstacles, start, and end positions.

    Args:
        grid: The grid to clone.

    Returns:
        A new Grid instance with identical configuration.
    """
    new_grid = Grid(
        grid.width, grid.height, grid.allow_diagonal, grid.diagonal_cost
    )

    # Copy obstacles
    for row in range(grid.height):
        for col in range(grid.width):
            node = grid.get_node(row, col)
            if node and node.state == NodeState.OBSTACLE:
                new_grid.add_obstacle(row, col)

    # Copy start and end
    if grid.start_node:
        new_grid.set_start(grid.start_node.row, grid.start_node.col)
    if grid.end_node:
        new_grid.set_end(grid.end_node.row, grid.end_node.col)

    return new_grid


def compare_algorithms(
    algorithms: List[PathfindingAlgorithm],
    grid_sizes: List[tuple[int, int]] | None = None,
    obstacle_densities: List[float] | None = None,
) -> Dict[str, List[AlgorithmMetrics]]:
    """
    Compare multiple algorithms across different scenarios.

    All algorithms are tested on the same grid configuration for each scenario,
    ensuring a fair comparison with identical obstacles.

    Args:
        algorithms: List of algorithm instances to compare.
        grid_sizes: List of (width, height) tuples to test.
        obstacle_densities: List of obstacle densities to test.

    Returns:
        Dictionary mapping algorithm names to lists of metrics.
    """
    if grid_sizes is None:
        grid_sizes = [(20, 20), (50, 50)]
    if obstacle_densities is None:
        obstacle_densities = [0.1, 0.3, 0.5]

    # Initialize results dictionary for all algorithms
    results: Dict[str, List[AlgorithmMetrics]] = {}
    for algorithm in algorithms:
        algorithm_name = algorithm.__class__.__name__
        results[algorithm_name] = []

    # Outer loops: grid sizes and densities
    # This ensures all algorithms use the same obstacles for each scenario
    for width, height in grid_sizes:
        for density in obstacle_densities:
            # Create ONE grid for this scenario with random obstacles
            base_grid = Grid(width, height)
            base_grid.add_obstacles_random(density=density)
            base_grid.set_start(0, 0)
            base_grid.set_end(width - 1, height - 1)

            # Test all algorithms on this same grid
            for algorithm in algorithms:
                # Clone the grid for this algorithm
                test_grid = clone_grid(base_grid)

                # Create new algorithm instance with cloned grid
                algo_class = algorithm.__class__
                algo_name = algo_class.__name__

                # Preserve AStar heuristic if present
                if algo_name == "AStar" and hasattr(algorithm, "heuristic_name"):
                    heuristic = algorithm.heuristic_name
                    test_algorithm = algo_class(test_grid, heuristic=heuristic)
                else:
                    test_algorithm = algo_class(test_grid)

                # Measure performance
                metrics = measure_algorithm(test_algorithm)
                results[algo_name].append(metrics)

    return results


def print_comparison(results: Dict[str, List[AlgorithmMetrics]]) -> None:
    """
    Print a formatted comparison of algorithm results.

    Args:
        results: Dictionary mapping algorithm names to lists of metrics.
    """
    print("\n" + "=" * 80)
    print("Algorithm Performance Comparison")
    print("=" * 80)

    for algo_name, metrics_list in results.items():
        print(f"\n{algo_name}:")
        print("-" * 80)

        if not metrics_list:
            print("  No results")
            continue

        # Calculate averages
        avg_time = sum(m.execution_time for m in metrics_list) / len(metrics_list)
        avg_visited = sum(m.nodes_visited for m in metrics_list) / len(metrics_list)
        avg_path_length = sum(m.path_length for m in metrics_list) / len(metrics_list)
        success_rate = sum(1 for m in metrics_list if m.path_found) / len(metrics_list)

        print(f"  Average Execution Time: {avg_time:.4f}s")
        print(f"  Average Nodes Visited: {avg_visited:.0f}")
        print(f"  Average Path Length: {avg_path_length:.2f}")
        print(f"  Success Rate: {success_rate * 100:.1f}%")

        # Show individual results
        print("\n  Individual Results:")
        for i, metrics in enumerate(metrics_list, 1):
            print(
                f"    Test {i}: time={metrics.execution_time:.4f}s, "
                f"visited={metrics.nodes_visited}, "
                f"path_length={metrics.path_length}, "
                f"found={metrics.path_found}"
            )

    print("\n" + "=" * 80)

