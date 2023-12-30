[![Run tests](https://github.com/ayaranitram/unyts/actions/workflows/test-package.yml/badge.svg)](https://github.com/ayaranitram/unyts/actions/workflows/test-package.yml)
[![PyPI version](https://img.shields.io/pypi/v/unyts.svg)](https://pypi.org/project/unyts/)
[![PyPI versions](https://img.shields.io/pypi/pyversions/unyts.svg)](https://pypi.org/project/unyts//)
[![PyPI license](https://img.shields.io/pypi/l/unyts.svg)](https://pypi.org/project/unyts/)

# `unyts`
  
After culminating a project for a class from MITx courses, I saw the opportunity to use a *digraph network* to build a units converter able to convert from any units to any units without the need to populate a huge but finite table of possible conversions. Powered by the _Breadth First Search_, or _BFS_, algorithm to search through the network, this converter can find conversions from a particular Unit (or ratio of units) to any other Unit (or ratio) as long as a path connecting them exists.

This package is under development and is regularly updated. Back compatibility is intended to be maintained when possible.
  
## What do this package contains:
- It is loaded with a network of units preloaded for distances, area, volume, mass and time conversions defined for SI and Imperial systems according to the definition of each Unit, i.e.: _1_foot = 12_inches_.
- Prefixes applied to the basic units, like in SI units _k_ to _m_ to make _km_, are loaded as a network of conversion paths allowing the algorithm to apply the prefix to any other unit in the same system.
- It provides a class _Unit_ powered with arithmetic and logic operations to intrinsically consider unit conversions when making calculations.  
  
## How to use this package:
This package is intended to be used in two ways:  
- Calling the function `units()` to define instances of the __Units__ class, that holds _values associated to units_, or, _quantities_.  
- As unit converter with the function `convert()` to explicitly make conversion of numeric variables and instances.  
  
### To use the _units converter_ function `convert()`:  
`from unyts import convert`  
`convert(value, from_units, to_units)`  
where:  
- _value_ is a number (int, float, numpy.array, etc)  
- *from_units* is a string defining the units of _value_ (i.e.: 'ft')  
- *to_units* is a string representing the units to convert _value_ (i.e.: 'km')  
  
### To create instances of the _Unit_ class using the `units()` function:  
`from unyts import units`  
`variable = units(value, units)`  
- _value_ is a number (`int`, `float`, `numpy.array`, etc)
- _units_ is a string defining the units of _value_ (i.e.: 'ft')

Then simply operate with the **Unit** instances or the variables related to them:  
 In: units(6, 'in') + units(1, 'ft')  
Out: 18_in  

### Referring to the `Unit` class:
`from unyts import Unit`  
- The `Unit` class is not intended to be used to create **Unit _instances_**, but to allow checking if other object `isinstance` of **Unit**: i.e.: `isinstance(variable, Unit)`  
- In order to create instances of **Unit** it is convenient to use the `units()` function as it will return the appropriate **Unit _subclass_**.  
  
### Uses examples:  
For further examples of use, the following Jupyter notebook <a href="https://github.com/ayaranitram/unyts/blob/master/unyts_demo.ipynb">**unyts_demo**</a> intends to be a guide on how to use this converter and units classes.  
  
## To install this package:  
Install it from the <a href="https://pypi.org/search/?q=unyts">pypi.org</a> repository:  
`pip install unyts`  
or upgrade to the latest version:  
`pip install --upgrade unyts`  
  
## Optional requisites:  
The main functionalities are purely Python powered and does not require any other package to work but, if present, some commonly known packages are used to improve the operability of `unyts`:  
- `NumPy` to be able to deal with iterables not of nparray type, like (list of values)  
- `Pandas` to be able to recognize Series and DataFrames  
- `cloudpickle` to be able to save internal dictionaries and network to cache file, for faster loading  
- `openpyxl` if willing to export the units network to a pandas DataFrame  
