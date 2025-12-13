"""Heuristic functions for A* algorithm."""

from typing import Callable

from src.graph.node import Node


def manhattan_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Manhattan distance (L1 norm) between two nodes.

    This heuristic is admissible for grid-based pathfinding with only
    orthogonal movement. It's also consistent (monotonic).

    Args:
        node1: First node.
        node2: Second node.

    Returns:
        Manhattan distance between the nodes.
    """
    return abs(node1.row - node2.row) + abs(node1.col - node2.col)


def euclidean_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Euclidean distance (L2 norm) between two nodes.

    This heuristic is admissible for grid-based pathfinding with
    diagonal movement allowed. It's also consistent.

    Args:
        node1: First node.
        node2: Second node.

    Returns:
        Euclidean distance between the nodes.
    """
    dr = node1.row - node2.row
    dc = node1.col - node2.col
    return (dr * dr + dc * dc) ** 0.5


def chebyshev_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Chebyshev distance (L∞ norm) between two nodes.

    This heuristic is admissible for grid-based pathfinding with
    diagonal movement allowed. It's optimal when diagonal movement
    has the same cost as orthogonal movement.

    Args:
        node1: First node.
        node2: Second node.

    Returns:
        Chebyshev distance between the nodes.
    """
    return max(abs(node1.row - node2.row), abs(node1.col - node2.col))


# Dictionary mapping heuristic names to functions
HEURISTICS: dict[str, Callable[[Node, Node], float]] = {
    "manhattan": manhattan_distance,
    "euclidean": euclidean_distance,
    "chebyshev": chebyshev_distance,
}


def get_heuristic(name: str) -> Callable[[Node, Node], float]:
    """
    Get a heuristic function by name.

    Args:
        name: Name of the heuristic ("manhattan", "euclidean", or "chebyshev").

    Returns:
        The heuristic function.

    Raises:
        ValueError: If the heuristic name is not recognized.
    """
    if name.lower() not in HEURISTICS:
        raise ValueError(
            f"Unknown heuristic: {name}. "
            f"Available heuristics: {list(HEURISTICS.keys())}"
        )
    return HEURISTICS[name.lower()]

