#!/usr/bin/env python3
"""Extract and categorize all recognized units for the manual appendix."""

from unyts.dictionaries import _all_units
from unyts.unit_class import Length, Mass, Time, Energy, Force, Temperature, Unitless
import json

# Get all units
all_units = sorted(_all_units())
print(f"Total units recognized: {len(all_units)}\n")

# Categorize units
categories = {
    'Length': [],
    'Mass': [],
    'Time': [],
    'Energy': [],
    'Force': [],
    'Temperature': [],
    'Unitless': [],
    'Other': []
}

for unit in all_units:
    try:
        from unyts import units as unit_factory
        u = unit_factory(1, unit)
        unit_type = type(u).__name__
        
        if unit_type in categories:
            categories[unit_type].append(unit)
        else:
            categories['Other'].append(unit)
    except:
        categories['Other'].append(unit)

# Print categorized units
for category in ['Length', 'Mass', 'Time', 'Energy', 'Force', 'Temperature', 'Unitless', 'Other']:
    if categories[category]:
        print(f"\n{category.upper()} ({len(categories[category])} units):")
        print(", ".join(sorted(categories[category])))
