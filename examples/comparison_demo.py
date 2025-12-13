"""Side-by-side comparison of different pathfinding algorithms."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.algorithms import AStar, Dijkstra
from src.graph import Grid
from src.visualization import Comparator


def main():
    """Run algorithm comparison demonstration."""
    print("=" * 80)
    print("Algorithm Comparison Demonstration")
    print("=" * 80)
    print("\nComparing:")
    print("  1. Dijkstra's Algorithm")
    print("  2. A* with Manhattan Heuristic")
    print("  3. A* with Euclidean Heuristic")
    print("  4. A* with Chebyshev Heuristic")
    print("\nCreating test grid...\n")

    # Create grid with obstacles
    grid = Grid(40, 40)
    grid.add_obstacles_random(density=0.25)
    grid.set_start(0, 0)
    grid.set_end(39, 39)

    # Create algorithm instances
    dijkstra = Dijkstra(grid)
    astar_manhattan = AStar(grid, heuristic="manhattan")
    astar_euclidean = AStar(grid, heuristic="euclidean")
    astar_chebyshev = AStar(grid, heuristic="chebyshev")

    algorithms = [dijkstra, astar_manhattan, astar_euclidean, astar_chebyshev]

    # Create comparator
    comparator = Comparator(grid, algorithms)

    print("Running step-by-step comparison...")
    print("(This will show how each algorithm explores the search space)\n")
    comparator.compare_step_by_step(interval=20)

    print("\nShowing final results comparison...")
    comparator.compare_final()


if __name__ == "__main__":
    main()

