"""Interactive demonstration allowing users to place obstacles and run algorithms."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.algorithms import AStar
from src.graph import Grid
from src.visualization import InteractiveVisualizer


def main():
    """Run interactive pathfinding demonstration."""
    print("=" * 80)
    print("Interactive Pathfinding Visualization")
    print("=" * 80)
    print("\nControls:")
    print("  'o' - Toggle obstacles (click on grid)")
    print("  's' - Set start position (click on grid)")
    print("  'e' - Set end position (click on grid)")
    print("  'r' - Run A* algorithm")
    print("  'c' - Clear all obstacles and reset")
    print("  ESC - Close visualization")
    print("\nStarting interactive visualization...\n")

    # Create grid
    grid = Grid(40, 40)
    grid.set_start(5, 5)
    grid.set_end(35, 35)

    # Create interactive visualizer with A* algorithm
    visualizer = InteractiveVisualizer(grid, AStar)
    visualizer.show()


if __name__ == "__main__":
    main()

