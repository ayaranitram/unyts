#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.3.0'
__release__ = 20250504
__all__ = ['logger']

# logger code generated with Claude.AI

import logging
import sys
import os
from IPython import get_ipython


class ColorCodes:
    """ANSI color codes for console output"""
    RESET = "\033[0m"
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Bright/bold versions
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class UnytsLogger:
    """Logger that works both in Jupyter notebook with HTML styling and in console with ANSI colors"""

    LOG_LEVELS = {
        "debug": (logging.DEBUG, "#e6f3ff", "#0066cc", ColorCodes.BRIGHT_CYAN),  # Light blue
        "info": (logging.INFO, "#e6ffe6", "#006600", ColorCodes.BRIGHT_GREEN),  # Light green
        "warning": (logging.WARNING, "#fff9e6", "#996600", ColorCodes.BRIGHT_YELLOW),  # Light yellow
        "error": (logging.ERROR, "#ffe6e6", "#cc0000", ColorCodes.BRIGHT_RED),  # Light red
        "critical": (logging.CRITICAL, "#f9e6ff", "#660066", ColorCodes.BRIGHT_MAGENTA)  # Light purple
    }

    def __init__(self, name="Unyts", default_level="info"):
        """Initialize the hybrid logger

        Args:
            name (str): Name of the logger
            default_level (str): Default log level (debug, info, warning, error, critical)
        """
        self.logger = logging.getLogger(name)
        self.output_id = f"logger_{id(self)}"
        self.is_notebook = self._is_jupyter_notebook()

        # Clear any existing handlers if the logger already exists
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Create output container if in notebook
        if self.is_notebook:
            self._setup_jupyter_container()

        # Set initial level
        self.set_level(default_level)

    def _is_jupyter_notebook(self):
        """Determine if code is running in a Jupyter notebook"""
        try:
            ipython = get_ipython()
            if ipython is not None and 'IPython.core.interactiveshell' in str(type(ipython)):
                # Check if it's notebook or terminal IPython
                if 'IPKernelApp' in ipython.config:
                    return True
                else:
                    return False
            else:
                return False
        except (ImportError, NameError):
            return False

    def _setup_jupyter_container(self):
        """Set up the HTML container for Jupyter output"""
        from IPython.display import display, HTML

        display(HTML(f"""
        <div id="{self.output_id}" style="font-family: monospace;">
        </div>
        <script>
            // Function to update the log container
            window.updateLog_{self.output_id} = function(color, textColor, level, message) {{
                const container = document.getElementById("{self.output_id}");
                if (container) {{
                    const logLine = document.createElement("div");
                    logLine.style.backgroundColor = color;
                    logLine.style.color = textColor;
                    logLine.style.padding = "1px 5px";
                    logLine.style.margin = "0";
                    logLine.style.lineHeight = "1.0";
                    logLine.innerHTML = `<b>[${level}]</b>: ${message}`;
                    container.appendChild(logLine);
                }}
            }};
        </script>
        """))

    def set_level(self, level_name):
        """Change the logger's level based on a string name

        Args:
            level_name (str): Log level name (debug, info, warning, error, critical)

        Returns:
            bool: True if level was changed successfully, False otherwise
        """
        level_name = level_name.lower()
        if level_name not in self.LOG_LEVELS:
            if self.is_notebook:
                self._log_jupyter_message(
                    f"Invalid log level: '{level_name}'. Using current level.",
                    "warning"
                )
            else:
                self._log_console_message(
                    f"Invalid log level: '{level_name}'. Using current level.",
                    "warning"
                )
            return False

        level_value = self.LOG_LEVELS[level_name][0]
        self.logger.setLevel(level_value)

        if self.is_notebook:
            self._log_jupyter_message(f"Log level changed to {level_name.upper()}", level_name)
        else:
            self._log_console_message(f"Log level changed to {level_name.upper()}", level_name)
        return True

    def get_current_level(self):
        """Get the current log level name

        Returns:
            str: Current log level name in uppercase
        """
        current_level = self.logger.getEffectiveLevel()
        for name, (level, _, _, _) in self.LOG_LEVELS.items():
            if level == current_level:
                return name.upper()
        return "UNKNOWN"

    def _log_jupyter_message(self, message, level):
        """Add a message to the log container using JavaScript

        Args:
            message (str): Log message text
            level (str): Log level name
        """
        from IPython.display import display_javascript

        level = level.lower()
        if level in self.LOG_LEVELS:
            _, bg_color, text_color, _ = self.LOG_LEVELS[level]
        else:
            # Default colors if level not found
            bg_color, text_color = "#ffffff", "#000000"

        # Escape any quotes in the message to prevent JS errors
        message = message.replace('"', '\\"').replace("'", "\\'")

        # Use JavaScript to append the message to the existing container
        js_code = f"""
        window.updateLog_{self.output_id}("{bg_color}", "{text_color}", "{level.upper()}", "{message}");
        """
        display_javascript(js_code, raw=True)

    def _log_console_message(self, message, level):
        """Print a colored message to the console

        Args:
            message (str): Log message text
            level (str): Log level name
        """
        level = level.lower()
        if level in self.LOG_LEVELS:
            _, _, _, color_code = self.LOG_LEVELS[level]
        else:
            color_code = ColorCodes.RESET

        print(f"{color_code}[{level.upper()}]: {message}{ColorCodes.RESET}")

    def _log_message(self, message, level):
        """Log a message to either Jupyter or console based on environment

        Args:
            message (str): Log message text
            level (str): Log level name
        """
        if self.is_notebook:
            self._log_jupyter_message(message, level)
        else:
            self._log_console_message(message, level)

    # Log methods
    def debug(self, message):
        """Log a debug message

        Args:
            message (str): Debug message text
        """
        if self.logger.isEnabledFor(logging.DEBUG):
            self._log_message(message, "debug")

    def info(self, message):
        """Log an info message

        Args:
            message (str): Info message text
        """
        if self.logger.isEnabledFor(logging.INFO):
            self._log_message(message, "info")

    def warning(self, message):
        """Log a warning message

        Args:
            message (str): Warning message text
        """
        if self.logger.isEnabledFor(logging.WARNING):
            self._log_message(message, "warning")

    def error(self, message):
        """Log an error message

        Args:
            message (str): Error message text
        """
        if self.logger.isEnabledFor(logging.ERROR):
            self._log_message(message, "error")

    def critical(self, message):
        """Log a critical message

        Args:
            message (str): Critical message text
        """
        if self.logger.isEnabledFor(logging.CRITICAL):
            self._log_message(message, "critical")

    def change_level_interactive(self):
        """Interactive function to change log level

        Returns:
            bool: True if level was changed successfully, False otherwise
        """
        print("\nAvailable log levels:")
        for i, level in enumerate(self.LOG_LEVELS.keys(), 1):
            print(f"{i}. {level.upper()}")

        try:
            choice = input("\nEnter log level (name or number): ")

            # Handle numeric input
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(self.LOG_LEVELS):
                    level_name = list(self.LOG_LEVELS.keys())[index]
                    return self.set_level(level_name)

            # Handle text input
            return self.set_level(choice)

        except Exception as e:
            self._log_message(f"Error changing log level: {e}", "error")
            return False


logger = UnytsLogger("Unyts")
