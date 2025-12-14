"""Animated step-by-step visualization of pathfinding algorithms."""

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import NodeState


class Animator:
    """
    Creates animated visualizations of pathfinding algorithms.

    Shows the step-by-step exploration of nodes, highlighting visited nodes,
    frontier nodes, and the final path in real-time.
    """

    def __init__(
        self,
        algorithm: PathfindingAlgorithm,
        grid: Grid,
        interval: int = 50,
        figsize: tuple[int, int] = (10, 10),
    ):
        """
        Initialize the animator.

        Args:
            algorithm: The pathfinding algorithm to visualize.
            grid: The grid on which the algorithm operates.
            interval: Animation interval in milliseconds.
            figsize: Figure size (width, height) in inches.
        """
        self.algorithm = algorithm
        self.grid = grid
        self.interval = interval
        self.figsize = figsize

        self.fig: plt.Figure | None = None
        self.ax: plt.Axes | None = None
        self.im: plt.AxesImage | None = None
        self.animation: animation.FuncAnimation | None = None

        # Color mapping for node states
        self.colors = {
            NodeState.UNVISITED: 1.0,  # White
            NodeState.VISITED: 0.6,  # Blue
            NodeState.FRONTIER: 0.8,  # Yellow
            NodeState.PATH: 0.2,  # Green
            NodeState.OBSTACLE: 0.0,  # Black
            NodeState.START: 0.4,  # Cyan
            NodeState.END: 0.3,  # Magenta
        }

    def _create_grid_image(self) -> np.ndarray:
        """
        Create a 2D array representation of the grid for visualization.

        Returns:
            2D numpy array with values corresponding to node states.
        """
        image = np.zeros((self.grid.height, self.grid.width))

        for row in range(self.grid.height):
            for col in range(self.grid.width):
                node = self.grid.get_node(row, col)
                if node:
                    image[row, col] = self.colors.get(node.state, 1.0)

        return image

    def _update_frame(self, frame: int) -> list:
        """
        Update function for matplotlib animation.

        Args:
            frame: Current frame number.

        Returns:
            List of artists to update.
        """
        if not self.algorithm.is_complete:
            self.algorithm.step()
        elif self.animation:
            # Stop animation when algorithm is complete
            self.animation.event_source.stop()

        # Update the image
        if self.im:
            self.im.set_array(self._create_grid_image())

        return [self.im] if self.im else []

    def animate(self, save_path: str | None = None) -> None:
        """
        Start the animation.

        Args:
            save_path: Optional path to save the animation as a GIF or video.
        """
        # Reset algorithm
        self.algorithm.reset()
        self.grid.reset()
        
        # Initialize algorithm (sets up start node in priority queue, etc.)
        self.algorithm.initialize()

        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_title(
            f"{self.algorithm.__class__.__name__} Algorithm Visualization",
            fontsize=14,
            fontweight="bold",
        )
        self.ax.set_xlabel("Column")
        self.ax.set_ylabel("Row")

        # Create initial image
        initial_image = self._create_grid_image()
        self.im = self.ax.imshow(
            initial_image,
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
            interpolation="nearest",
            aspect="equal",
        )

        # Add colorbar with labels
        cbar = self.fig.colorbar(self.im, ax=self.ax, ticks=[0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0])
        cbar.set_ticklabels(
            ["Obstacle", "Path", "End", "Start", "Visited", "Frontier", "Unvisited"]
        )

        # Create animation
        self.animation = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            interval=self.interval,
            blit=True,
            repeat=False,
            cache_frame_data=False,
        )

        # Save if requested
        if save_path:
            if save_path.endswith(".gif"):
                self.animation.save(save_path, writer="pillow", fps=1000 // self.interval)
            else:
                self.animation.save(save_path, fps=1000 // self.interval)

        plt.tight_layout()
        plt.show()

    def show_final(self) -> None:
        """
        Show the final state of the algorithm without animation.
        """
        # Run algorithm to completion
        self.algorithm.find_path()

        # Create figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_title(
            f"{self.algorithm.__class__.__name__} - Final Result",
            fontsize=14,
            fontweight="bold",
        )
        self.ax.set_xlabel("Column")
        self.ax.set_ylabel("Row")

        # Create image
        final_image = self._create_grid_image()
        self.im = self.ax.imshow(
            final_image,
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
            interpolation="nearest",
            aspect="equal",
        )

        # Add colorbar
        cbar = self.fig.colorbar(self.im, ax=self.ax, ticks=[0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0])
        cbar.set_ticklabels(
            ["Obstacle", "Path", "End", "Start", "Visited", "Frontier", "Unvisited"]
        )

        # Add metrics text
        metrics = self.algorithm.get_metrics()
        metrics_text = (
            f"Nodes Visited: {metrics['nodes_visited']}\n"
            f"Path Length: {metrics['path_length']}\n"
            f"Path Found: {metrics['path_found']}"
        )
        self.ax.text(
            0.02,
            0.98,
            metrics_text,
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        plt.tight_layout()
        plt.show()

