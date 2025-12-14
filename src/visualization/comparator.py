"""Side-by-side comparison of multiple pathfinding algorithms."""

import matplotlib.pyplot as plt
import numpy as np

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import NodeState


class Comparator:
    """
    Compare multiple algorithms side-by-side on the same grid.

    Displays synchronized visualizations showing how different algorithms
    explore the search space and find paths.
    """

    def __init__(
        self,
        grid: Grid,
        algorithms: list[PathfindingAlgorithm],
        figsize: tuple[int, int] = (16, 8),
    ):
        """
        Initialize the comparator.

        Args:
            grid: The grid to use for comparison (will be cloned for each algorithm).
            algorithms: List of algorithm instances to compare.
            figsize: Figure size (width, height) in inches.
        """
        self.original_grid = grid
        self.algorithms = algorithms
        self.figsize = figsize

        # Create separate grids for each algorithm
        self.grids: list[Grid] = []
        for _ in algorithms:
            new_grid = Grid(grid.width, grid.height, grid.allow_diagonal, grid.diagonal_cost)
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
            self.grids.append(new_grid)

        # Update algorithms to use their respective grids
        for i, algo in enumerate(self.algorithms):
            algo.grid = self.grids[i]

        self.fig: plt.Figure | None = None
        self.axes: list[plt.Axes] = []
        self.images: list[plt.AxesImage] = []

        # Color mapping
        self.colors = {
            NodeState.UNVISITED: 1.0,
            NodeState.VISITED: 0.6,
            NodeState.FRONTIER: 0.8,
            NodeState.PATH: 0.2,
            NodeState.OBSTACLE: 0.0,
            NodeState.START: 0.4,
            NodeState.END: 0.3,
        }

    def _create_grid_image(self, grid: Grid) -> np.ndarray:
        """Create a 2D array representation of a grid."""
        image = np.zeros((grid.height, grid.width))

        for row in range(grid.height):
            for col in range(grid.width):
                node = grid.get_node(row, col)
                if node:
                    image[row, col] = self.colors.get(node.state, 1.0)

        return image

    def _update_all_displays(self) -> None:
        """Update all algorithm visualizations."""
        for i, (grid, im) in enumerate(zip(self.grids, self.images)):
            im.set_array(self._create_grid_image(grid))

        self.fig.canvas.draw_idle()

    def compare_step_by_step(self, interval: int = 50) -> None:
        """
        Compare algorithms step-by-step with synchronized visualization.

        Args:
            interval: Delay between steps in milliseconds.
        """
        # Reset all algorithms
        for algo in self.algorithms:
            algo.reset()
        for grid in self.grids:
            grid.reset()
        
        # Initialize all algorithms (sets up start node in priority queue, etc.)
        for algo in self.algorithms:
            algo.initialize()

        # Create figure with subplots
        num_algorithms = len(self.algorithms)
        self.fig, self.axes = plt.subplots(1, num_algorithms, figsize=self.figsize)

        if num_algorithms == 1:
            self.axes = [self.axes]

        self.images = []

        # Initialize each subplot
        for i, (algo, ax) in enumerate(zip(self.algorithms, self.axes)):
            grid = self.grids[i]
            initial_image = self._create_grid_image(grid)

            im = ax.imshow(
                initial_image,
                cmap="viridis",
                vmin=0.0,
                vmax=1.0,
                interpolation="nearest",
                aspect="equal",
            )
            self.images.append(im)

            algo_name = algo.__class__.__name__
            if hasattr(algo, "heuristic_name"):
                algo_name += f" ({algo.heuristic_name})"
            ax.set_title(algo_name, fontsize=12, fontweight="bold")
            ax.set_xlabel("Column")
            ax.set_ylabel("Row")

        # Add shared colorbar
        cbar = self.fig.colorbar(
            self.images[0], ax=self.axes, ticks=[0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]
        )
        cbar.set_ticklabels(
            ["Obstacle", "Path", "End", "Start", "Visited", "Frontier", "Unvisited"]
        )

        # Main comparison loop
        all_complete = False
        step_count = 0
        max_steps = self.original_grid.width * self.original_grid.height * 2

        while not all_complete and step_count < max_steps:
            all_complete = True

            # Step each algorithm
            for algo in self.algorithms:
                if not algo.is_complete:
                    algo.step()
                    all_complete = False

            # Update displays
            self._update_all_displays()
            plt.pause(interval / 1000.0)
            step_count += 1

        # Show final metrics
        for i, (algo, ax) in enumerate(zip(self.algorithms, self.axes)):
            metrics = algo.get_metrics()
            metrics_text = (
                f"Nodes Visited: {metrics['nodes_visited']}\n"
                f"Path Length: {metrics['path_length']}\n"
                f"Path Found: {metrics['path_found']}"
            )
            ax.text(
                0.02,
                0.98,
                metrics_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
            )

        plt.suptitle("Algorithm Comparison - Final Results", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.show()

    def compare_final(self) -> None:
        """Compare algorithms by showing only their final results."""
        # Run all algorithms to completion
        for algo in self.algorithms:
            algo.find_path()

        # Create figure with subplots
        num_algorithms = len(self.algorithms)
        self.fig, self.axes = plt.subplots(1, num_algorithms, figsize=self.figsize)

        if num_algorithms == 1:
            self.axes = [self.axes]

        self.images = []

        # Display each algorithm's result
        for i, (algo, ax) in enumerate(zip(self.algorithms, self.axes)):
            grid = self.grids[i]
            final_image = self._create_grid_image(grid)

            im = ax.imshow(
                final_image,
                cmap="viridis",
                vmin=0.0,
                vmax=1.0,
                interpolation="nearest",
                aspect="equal",
            )
            self.images.append(im)

            algo_name = algo.__class__.__name__
            if hasattr(algo, "heuristic_name"):
                algo_name += f" ({algo.heuristic_name})"
            ax.set_title(algo_name, fontsize=12, fontweight="bold")
            ax.set_xlabel("Column")
            ax.set_ylabel("Row")

            # Add metrics
            metrics = algo.get_metrics()
            metrics_text = (
                f"Nodes Visited: {metrics['nodes_visited']}\n"
                f"Path Length: {metrics['path_length']}\n"
                f"Path Found: {metrics['path_found']}"
            )
            ax.text(
                0.02,
                0.98,
                metrics_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
            )

        # Add shared colorbar
        cbar = self.fig.colorbar(
            self.images[0], ax=self.axes, ticks=[0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]
        )
        cbar.set_ticklabels(
            ["Obstacle", "Path", "End", "Start", "Visited", "Frontier", "Unvisited"]
        )

        plt.suptitle("Algorithm Comparison - Final Results", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.show()

