"""Basic demonstration of pathfinding algorithms with animated visualization."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.algorithms import AStar, Dijkstra
from src.graph import Grid
from src.visualization import Animator


def main():
    """Run basic demonstrations of pathfinding algorithms."""
    print("Creating grid with obstacles...")
    grid = Grid(50, 50)
    grid.add_obstacles_random(density=0.3)
    grid.set_start(0, 0)
    grid.set_end(49, 49)

    print("\n" + "=" * 80)
    print("Demonstrating A* Algorithm with Manhattan Heuristic")
    print("=" * 80)
    astar = AStar(grid, heuristic="manhattan")
    animator = Animator(astar, grid, interval=30)
    animator.animate()

    print("\n" + "=" * 80)
    print("Demonstrating Dijkstra's Algorithm")
    print("=" * 80)
    dijkstra = Dijkstra(grid)
    animator = Animator(dijkstra, grid, interval=30)
    animator.animate()

    print("\n" + "=" * 80)
    print("Demonstrating A* Algorithm with Euclidean Heuristic")
    print("=" * 80)
    astar_euclidean = AStar(grid, heuristic="euclidean")
    animator = Animator(astar_euclidean, grid, interval=30)
    animator.animate()


if __name__ == "__main__":
    main()

