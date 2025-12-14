"""Generate JSON data from algorithm execution for web visualization."""

from typing import Any, Dict, List

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import Node, NodeState


def grid_to_dict(grid: Grid) -> Dict[str, Any]:
    """
    Convert a grid to a dictionary representation.

    Args:
        grid: The grid to convert.

    Returns:
        Dictionary containing grid configuration.
    """
    obstacles: List[List[int]] = []
    for row in range(grid.height):
        for col in range(grid.width):
            node = grid.get_node(row, col)
            if node and node.state == NodeState.OBSTACLE:
                obstacles.append([row, col])

    start: List[int] | None = None
    if grid.start_node:
        start = [grid.start_node.row, grid.start_node.col]

    end: List[int] | None = None
    if grid.end_node:
        end = [grid.end_node.row, grid.end_node.col]

    return {
        "width": grid.width,
        "height": grid.height,
        "obstacles": obstacles,
        "start": start,
        "end": end,
        "allow_diagonal": grid.allow_diagonal,
    }


def get_node_states(grid: Grid) -> Dict[str, List[List[int]]]:
    """
    Get current state of all nodes in the grid.

    Args:
        grid: The grid to analyze.

    Returns:
        Dictionary with lists of node coordinates by state.
    """
    visited: List[List[int]] = []
    frontier: List[List[int]] = []
    path: List[List[int]] = []

    for row in range(grid.height):
        for col in range(grid.width):
            node = grid.get_node(row, col)
            if not node:
                continue

            coord = [row, col]

            if node.state == NodeState.VISITED:
                visited.append(coord)
            elif node.state == NodeState.FRONTIER:
                frontier.append(coord)
            elif node.state == NodeState.PATH:
                path.append(coord)

    return {
        "visited": visited,
        "frontier": frontier,
        "path": path if path else None,
    }


def capture_algorithm_steps(
    algorithm: PathfindingAlgorithm, grid: Grid
) -> List[Dict[str, Any]]:
    """
    Capture algorithm execution step-by-step.

    Args:
        algorithm: The algorithm to execute.
        grid: The grid on which the algorithm runs.

    Returns:
        List of step dictionaries, each containing the state at that step.
    """
    # Reset everything
    algorithm.reset()
    grid.reset()
    algorithm.initialize()

    steps: List[Dict[str, Any]] = []
    step_count = 0
    max_steps = grid.width * grid.height * 2  # Safety limit

    # Capture initial state
    node_states = get_node_states(grid)
    steps.append(
        {
            "step": step_count,
            "visited": node_states["visited"],
            "frontier": node_states["frontier"],
            "path": node_states["path"],
        }
    )

    # Execute algorithm step by step
    while not algorithm.is_complete and step_count < max_steps:
        algorithm.step()
        step_count += 1

        # Capture state after this step
        node_states = get_node_states(grid)
        steps.append(
            {
                "step": step_count,
                "visited": node_states["visited"],
                "frontier": node_states["frontier"],
                "path": node_states["path"],
            }
        )

    return steps


def algorithm_to_dict(algorithm: PathfindingAlgorithm, grid: Grid) -> Dict[str, Any]:
    """
    Convert algorithm execution to dictionary format for JSON export.

    Args:
        algorithm: The algorithm to convert.
        grid: The grid on which the algorithm ran.

    Returns:
        Dictionary containing algorithm name, steps, and metrics.
    """
    # Get algorithm name
    algo_name = algorithm.__class__.__name__
    if hasattr(algorithm, "heuristic_name"):
        algo_name += f" ({algorithm.heuristic_name})"

    # Capture steps
    steps = capture_algorithm_steps(algorithm, grid)

    # Get final metrics
    metrics = algorithm.get_metrics()

    return {
        "name": algo_name,
        "steps": steps,
        "metrics": {
            "nodes_visited": metrics["nodes_visited"],
            "path_length": metrics["path_length"],
            "path_found": metrics["path_found"],
        },
    }


def generate_comparison_data(
    grid: Grid, algorithms: List[PathfindingAlgorithm]
) -> Dict[str, Any]:
    """
    Generate comparison data for multiple algorithms.

    Args:
        grid: The base grid (will be cloned for each algorithm).
        algorithms: List of algorithm instances to compare.

    Returns:
        Dictionary containing grid and algorithm data.
    """
    from src.graph.grid import Grid as GridClass

    # Create separate grids for each algorithm
    grids: List[GridClass] = []
    for _ in algorithms:
        new_grid = GridClass(
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
        grids.append(new_grid)

    # Update algorithms to use their respective grids
    for i, algo in enumerate(algorithms):
        algo.grid = grids[i]

    # Generate data for each algorithm
    algorithm_data = []
    for algo, algo_grid in zip(algorithms, grids):
        algo_data = algorithm_to_dict(algo, algo_grid)
        algorithm_data.append(algo_data)

    # Get grid data (use first grid as they're all the same structure)
    grid_data = grid_to_dict(grids[0])

    return {
        "grid": grid_data,
        "algorithms": algorithm_data,
    }

