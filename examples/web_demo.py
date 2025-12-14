"""Launch the web-based algorithm comparison visualization."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.web.api import run_server
import webbrowser
import threading
import time


def main():
    """Launch the web server and open browser."""
    print("=" * 80)
    print("Pathfinding Algorithm Comparison - Web Visualization")
    print("=" * 80)
    print("\nStarting web server...")
    print("The visualization will open in your default browser.")
    print("Press Ctrl+C to stop the server.\n")

    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5000")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Run server
    try:
        run_server(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")


if __name__ == "__main__":
    main()

