#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>

This module serves as the entry point for the Unyts package when run as a script. 
It starts the Unyts GUI application. The version and release information are defined here, 
and the main block calls the `start_gui` function imported from the package to launch the application.
"""

from unyts import start_gui

__version__ = '0.1.1'
__release__ = 20240319

if __name__ == '__main__':
    # start Unyts GUI
    start_gui()