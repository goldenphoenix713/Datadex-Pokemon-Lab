"""Main entry point for the Data-Dex Dash application.

This module initializes the Dash app by integrating modular components,
layouts, and callbacks from the src/ directory.
"""

import dash
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add("logs/app.log", level="DEBUG")
logger.add(sys.stderr, level="DEBUG")

# Enforce React 18.2.0 for DMC compatibility
dash._dash_renderer._set_react_version("18.2.0")  # type: ignore[possibly-missing-attribute]

# Initialize the Dash app
app = dash.Dash(__name__, title="Data-Dex: Ultimate Stat Lab")

# Import layout and callbacks to register them
from src.layout import layout  # noqa: E402
import src.callbacks  # noqa: E402, F401

app.layout = layout

if __name__ == "__main__":
    logger.info("Data-Dex Dash application starting...")
    # Start the server (debug=True enables hot reloading)
    app.run(debug=True, port=8050, use_reloader=False)
