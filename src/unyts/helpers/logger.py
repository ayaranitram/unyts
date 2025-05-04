#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 04 2025

@author: Martín Carlos Araya <martinaraya@gmail.com>

this logger was coded with help of Claude AI
"""

__version__ = '0.1.0'
__release__ = 20250504
__all__ = ['logger']

import logging
import sys
import os


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


class UnytLogger:
    """Logger that works in both Jupyter notebook and console with explicit mode control"""

    LOG_LEVELS = {
        "debug": (logging.DEBUG, "#e6f3ff", "#0066cc", ColorCodes.BRIGHT_CYAN),  # Light blue
        "info": (logging.INFO, "#e6ffe6", "#006600", ColorCodes.BRIGHT_GREEN),  # Light green
        "warning": (logging.WARNING, "#fff9e6", "#996600", ColorCodes.BRIGHT_YELLOW),  # Light yellow
        "error": (logging.ERROR, "#ffe6e6", "#cc0000", ColorCodes.BRIGHT_RED),  # Light red
        "critical": (logging.CRITICAL, "#f9e6ff", "#660066", ColorCodes.BRIGHT_MAGENTA)  # Light purple
    }

    def __init__(self, name="Unyt", default_level="info", mode=None):
        """Initialize the logger with explicit mode control

        Args:
            name (str): Name of the logger
            default_level (str): Default log level (debug, info, warning, error, critical)
            mode (str, optional): Force 'jupyter' or 'console' mode. If None, auto-detect.
        """
        self.logger = logging.getLogger(name)

        # Set display mode (jupyter, console) with option to force a specific mode
        if mode is not None and mode in ['jupyter', 'console']:
            self.mode = mode
        else:
            self.mode = 'jupyter' if self._is_notebook_safe() else 'console'

        # Verify jupyter mode actually works, otherwise fallback to console
        if self.mode == 'jupyter' and not self._can_display_html():
            self.mode = 'console'

        # Clear any existing handlers if the logger already exists
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Set initial level
        self.set_level(default_level)

    def _is_notebook_safe(self):
        """Simple check for Jupyter notebook environment"""
        try:
            # Check for specific environment variables that indicate Jupyter
            if 'JUPYTER_KERNEL' in os.environ or 'JPY_PARENT_PID' in os.environ:
                return True

            # Check if IPython is in sys.modules
            if 'IPython' in sys.modules:
                return True

            return False
        except:
            return False

    def _can_display_html(self):
        """Check if we can actually display HTML content in the current environment"""
        try:
            # Try to import display and HTML and see if they exist
            from IPython.display import display, HTML
            # Make a test HTML object to verify it works
            test_html = HTML("<div>Test</div>")
            return True
        except:
            return False

    def set_level(self, level_name):
        """Change the logger's level based on a string name

        Args:
            level_name (str): Log level name (debug, info, warning, error, critical)

        Returns:
            bool: True if level was changed successfully, False otherwise
        """
        level_name = level_name.lower()
        if level_name not in self.LOG_LEVELS:
            message = f"Invalid log level: '{level_name}'. Using current level."
            self._log_message(message, "warning")
            return False

        level_value = self.LOG_LEVELS[level_name][0]
        self.logger.setLevel(level_value)
        self._log_message(f"Log level changed to {level_name.upper()}", level_name)
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

    def force_console_mode(self):
        """Force logger to use console mode regardless of environment"""
        self.mode = 'console'

    def force_jupyter_mode(self):
        """Force logger to use jupyter mode if the environment supports it"""
        if self._can_display_html():
            self.mode = 'jupyter'
        else:
            self._log_console("Cannot use Jupyter mode in this environment", "warning")

    def _log_jupyter(self, message, level):
        """Display a message with HTML styling for Jupyter notebooks

        Args:
            message (str): Log message text
            level (str): Log level name
        """
        try:
            from IPython.display import display, HTML

            level = level.lower()
            if level in self.LOG_LEVELS:
                _, bg_color, text_color, _ = self.LOG_LEVELS[level]
            else:
                # Default colors if level not found
                bg_color, text_color = "#ffffff", "#000000"

            # Create HTML with styled div
            html = f"""
            <div style="
                background-color: {bg_color}; 
                color: {text_color}; 
                padding: 10px; 
                border-radius: 15px; 
                margin: 0px;
                font-family: monospace;
                line-height: 1.2;
                border: none;
            ">
                <b>[{level.upper()}]</b>: {message}
            </div>
            """
            display(HTML(html))
        except Exception:
            # Fall back to console if display fails
            self._log_console(message, level)

    def _log_console(self, message, level):
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
        """Route message to appropriate display method based on mode

        Args:
            message (str): Log message text
            level (str): Log level name
        """
        if self.mode == 'jupyter':
            self._log_jupyter(message, level)
        else:
            self._log_console(message, level)

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


# Create a default logger instance - force console mode for reliability
logger = UnytLogger("Unyt", mode=None)
