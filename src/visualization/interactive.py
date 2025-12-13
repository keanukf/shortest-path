"""Interactive visualization with obstacle placement and algorithm control."""

import matplotlib.pyplot as plt
import numpy as np

from src.algorithms.base import PathfindingAlgorithm
from src.graph.grid import Grid
from src.graph.node import NodeState


class InteractiveVisualizer:
    """
    Interactive visualization allowing users to place obstacles and run algorithms.

    Features:
    - Click to place/remove obstacles
    - Set start and end positions
    - Run algorithms with visualization
    - Reset grid
    """

    def __init__(
        self,
        grid: Grid,
        algorithm_class: type[PathfindingAlgorithm],
        figsize: tuple[int, int] = (12, 10),
    ):
        """
        Initialize the interactive visualizer.

        Args:
            grid: The grid to visualize.
            algorithm_class: Class of the algorithm to use.
            figsize: Figure size (width, height) in inches.
        """
        self.grid = grid
        self.algorithm_class = algorithm_class
        self.algorithm: PathfindingAlgorithm | None = None
        self.figsize = figsize

        self.fig: plt.Figure | None = None
        self.ax: plt.Axes | None = None
        self.im: plt.AxesImage | None = None

        # Interaction state
        self.mode = "obstacle"  # 'obstacle', 'start', 'end', 'run'
        self.is_running = False

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

    def _create_grid_image(self) -> np.ndarray:
        """Create a 2D array representation of the grid."""
        image = np.zeros((self.grid.height, self.grid.width))

        for row in range(self.grid.height):
            for col in range(self.grid.width):
                node = self.grid.get_node(row, col)
                if node:
                    image[row, col] = self.colors.get(node.state, 1.0)

        return image

    def _update_display(self) -> None:
        """Update the displayed grid."""
        if self.im:
            self.im.set_array(self._create_grid_image())
            self.fig.canvas.draw_idle()

    def _on_click(self, event) -> None:
        """Handle mouse click events."""
        if not event.inaxes or self.is_running:
            return

        # Convert click position to grid coordinates
        col = int(event.xdata + 0.5)
        row = int(event.ydata + 0.5)

        if not self.grid.is_valid_position(row, col):
            return

        node = self.grid.get_node(row, col)

        if self.mode == "obstacle":
            # Toggle obstacle
            if node.state == NodeState.OBSTACLE:
                self.grid.remove_obstacle(row, col)
            else:
                self.grid.add_obstacle(row, col)
        elif self.mode == "start":
            self.grid.set_start(row, col)
        elif self.mode == "end":
            self.grid.set_end(row, col)

        self._update_display()

    def _on_key(self, event) -> None:
        """Handle keyboard events."""
        if self.is_running:
            return

        if event.key == "o":
            self.mode = "obstacle"
            self.ax.set_title("Mode: Place/Remove Obstacles (Click on grid)", fontsize=12)
        elif event.key == "s":
            self.mode = "start"
            self.ax.set_title("Mode: Set Start Position (Click on grid)", fontsize=12)
        elif event.key == "e":
            self.mode = "end"
            self.ax.set_title("Mode: Set End Position (Click on grid)", fontsize=12)
        elif event.key == "r":
            self._run_algorithm()
        elif event.key == "c":
            self._clear_all()
        elif event.key == "escape":
            plt.close(self.fig)

        self.fig.canvas.draw_idle()

    def _run_algorithm(self) -> None:
        """Run the pathfinding algorithm with step-by-step visualization."""
        if not self.grid.start_node or not self.grid.end_node:
            self.ax.set_title(
                "Error: Please set start and end positions first! (Press 's' for start, 'e' for end)",
                fontsize=12,
                color="red",
            )
            self.fig.canvas.draw_idle()
            return

        self.is_running = True
        self.ax.set_title("Running algorithm...", fontsize=12)

        # Reset grid and create algorithm
        self.grid.reset()
        self.algorithm = self.algorithm_class(self.grid)

        # Run algorithm step by step
        step_count = 0
        max_steps = self.grid.width * self.grid.height * 2  # Safety limit

        while not self.algorithm.is_complete and step_count < max_steps:
            self.algorithm.step()
            self._update_display()
            step_count += 1
            plt.pause(0.01)  # Small delay for visualization

        # Show final result
        if self.algorithm.is_path_found:
            metrics = self.algorithm.get_metrics()
            self.ax.set_title(
                f"Path Found! (Visited: {metrics['nodes_visited']}, "
                f"Length: {metrics['path_length']}) - Press 'c' to clear, 'r' to rerun",
                fontsize=12,
                color="green",
            )
        else:
            self.ax.set_title(
                "No Path Found! - Press 'c' to clear, 'r' to rerun", fontsize=12, color="red"
            )

        self.is_running = False
        self.fig.canvas.draw_idle()

    def _clear_all(self) -> None:
        """Clear the grid and reset visualization."""
        self.grid.clear_obstacles()
        if self.grid.start_node:
            self.grid.start_node.state = NodeState.UNVISITED
            self.grid.start_node = None
        if self.grid.end_node:
            self.grid.end_node.state = NodeState.UNVISITED
            self.grid.end_node = None
        self.grid.reset()
        self.algorithm = None
        self.mode = "obstacle"
        self.ax.set_title(
            "Interactive Pathfinding - Press 'o' for obstacles, 's' for start, "
            "'e' for end, 'r' to run, 'c' to clear",
            fontsize=12,
        )
        self._update_display()

    def show(self) -> None:
        """Display the interactive visualization."""
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

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

        # Add colorbar
        cbar = self.fig.colorbar(
            self.im, ax=self.ax, ticks=[0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]
        )
        cbar.set_ticklabels(
            ["Obstacle", "Path", "End", "Start", "Visited", "Frontier", "Unvisited"]
        )

        # Set title with instructions
        self.ax.set_title(
            "Interactive Pathfinding - Press 'o' for obstacles, 's' for start, "
            "'e' for end, 'r' to run, 'c' to clear",
            fontsize=12,
        )
        self.ax.set_xlabel("Column")
        self.ax.set_ylabel("Row")

        # Add instructions text
        instructions = (
            "Controls:\n"
            "  'o' - Toggle obstacles\n"
            "  's' - Set start position\n"
            "  'e' - Set end position\n"
            "  'r' - Run algorithm\n"
            "  'c' - Clear all\n"
            "  ESC - Close"
        )
        self.ax.text(
            1.02,
            0.5,
            instructions,
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment="center",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        # Connect event handlers
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

        plt.tight_layout()
        plt.show()

