# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 22:21:57 2022

@author: martin
"""

from setuptools import setup, find_packages

setup(
      author="Martin Carlos Araya",
      description="a unit converter based on graph network and classes to operate with units.",
      name="unitconverter",
      version="0.1.0",
      packages=find_packages(include=['units, units.*']),
      install_requires=['numpy'],
      python_requires='>=3.5.0'
      )