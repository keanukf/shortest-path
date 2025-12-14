"""Flask API server for algorithm visualization."""

from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from src.algorithms import AStar, Dijkstra
from src.graph import Grid
from src.web.data_generator import generate_comparison_data


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask app instance.
    """
    app = Flask(__name__, static_folder=None)

    # Get paths
    project_root = Path(__file__).parent.parent.parent
    web_dir = project_root / "web"

    @app.route("/")
    def index() -> str:
        """Serve the main HTML page."""
        return send_from_directory(str(web_dir), "index.html")

    @app.route("/<path:filename>")
    def serve_static(filename: str) -> Any:
        """Serve static files (CSS, JS)."""
        return send_from_directory(str(web_dir), filename)

    @app.route("/api/compare", methods=["POST"])
    def compare_algorithms() -> Any:
        """
        Compare multiple algorithms on a grid.

        Request body should contain:
        - width: Grid width
        - height: Grid height
        - obstacles: List of [row, col] obstacle positions
        - start: [row, col] start position
        - end: [row, col] end position
        - algorithms: List of algorithm names to compare
        - allow_diagonal: Whether to allow diagonal movement (optional)

        Returns:
            JSON data with grid and algorithm comparison results.
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Extract grid configuration
            width = int(data.get("width", 40))
            height = int(data.get("height", 40))
            allow_diagonal = data.get("allow_diagonal", False)
            diagonal_cost = data.get("diagonal_cost", 1.414)

            # Set start and end first (before obstacles)
            start = data.get("start", [0, 0])
            end = data.get("end", [height - 1, width - 1])
            
            # Create grid
            grid = Grid(width, height, allow_diagonal, diagonal_cost)
            
            if len(start) == 2:
                grid.set_start(start[0], start[1])
            if len(end) == 2:
                grid.set_end(end[0], end[1])

            # Add obstacles
            obstacles = data.get("obstacles", [])
            density = data.get("density")
            
            if density is not None:
                # Generate random obstacles if density is provided
                grid.add_obstacles_random(density=density)
            else:
                # Add specific obstacles
                if isinstance(obstacles, list):
                    for obstacle in obstacles:
                        if len(obstacle) == 2:
                            grid.add_obstacle(obstacle[0], obstacle[1])

            # Create algorithms
            algorithm_names = data.get("algorithms", ["Dijkstra", "AStar"])
            algorithms = []

            for algo_name in algorithm_names:
                if algo_name == "Dijkstra":
                    algorithms.append(Dijkstra(grid))
                elif algo_name.startswith("AStar"):
                    # Parse heuristic if provided (e.g., "AStar:manhattan")
                    parts = algo_name.split(":")
                    heuristic = parts[1] if len(parts) > 1 else "manhattan"
                    algorithms.append(AStar(grid, heuristic=heuristic))
                else:
                    return (
                        jsonify({"error": f"Unknown algorithm: {algo_name}"}),
                        400,
                    )

            if not algorithms:
                return jsonify({"error": "No valid algorithms specified"}), 400

            # Generate comparison data
            comparison_data = generate_comparison_data(grid, algorithms)

            return jsonify(comparison_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/presets", methods=["GET"])
    def get_presets() -> Any:
        """
        Get predefined grid configurations.

        Returns:
            JSON with preset configurations.
        """
        presets = {
            "simple": {
                "width": 30,
                "height": 30,
                "obstacles": [],
                "start": [0, 0],
                "end": [29, 29],
                "allow_diagonal": False,
            },
            "maze": {
                "width": 40,
                "height": 40,
                "obstacles": [
                    # Create a simple maze pattern
                    *[[10, i] for i in range(5, 35)],
                    *[[20, i] for i in range(5, 35)],
                    *[[i, 15] for i in range(5, 15)],
                    *[[i, 25] for i in range(15, 25)],
                ],
                "start": [0, 0],
                "end": [39, 39],
                "allow_diagonal": False,
            },
            "random": {
                "width": 40,
                "height": 40,
                "obstacles": "random",  # Special marker for random generation
                "start": [0, 0],
                "end": [39, 39],
                "allow_diagonal": False,
                "density": 0.25,
            },
            "open_field": {
                "width": 50,
                "height": 50,
                "obstacles": [],
                "start": [5, 5],
                "end": [45, 45],
                "allow_diagonal": True,
            },
        }

        return jsonify(presets)

    return app


def run_server(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask development server.

    Args:
        host: Host to bind to.
        port: Port to bind to.
        debug: Enable debug mode.
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)

