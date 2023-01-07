[![Run tests](https://github.com/ayaranitram/unyts/actions/workflows/test-package.yml/badge.svg)](https://github.com/ayaranitram/unyts/actions/workflows/test-package.yml)
[![PyPI version](https://img.shields.io/pypi/v/unyts.svg)](https://pypi.org/project/unyts/)
[![PyPI versions](https://img.shields.io/pypi/pyversions/unyts.svg)](https://pypi.org/project/unyts//)
[![PyPI license](https://img.shields.io/pypi/l/unyts.svg)](https://pypi.org/project/unyts/)

# `unyts`

After culminating a project for a class from MITx courses, I saw the opportunity to use a *digraph network* to build a Unit converter able to convert from any units to any units without the need to populate a huge but finite table of possible conversions. Powered by the _Breadth First Search_, or _BFS_, algorithm to search through the network, this converter can find conversions from a particular Unit (or ratio of units) to any other Unit (or ratio) as long as a path connecting them exists.

This package is under development and is regularly updated. Back compatibility is intended to be maintained when possible.

## What Contains This Package
- It is loaded with a network of units preloaded for distances, area, volume, mass and time conversions defined for SI and Imperial systems according to the definition of each Unit, i.e.: _1_foot = 12_inches_.
- Prefixes applied to the basic units, like _k_ to _m_ to make _km_, are loaded as a network of Conversion paths allowing the algorithm to apply the prefix to any other Unit on the same system.
- It provides classes of _unit_ useful powered with arithmetic and logic operations to intrinsically consider Unit conversions when making calculations.

## How To Use It
This package is intended to be used in two ways:
- Using the function `units()` to define instances of the __Units__ class, holding _values with units_, or, _quantities_.
- As unit converter with the function `convert()` to explicitly make conversion of numeric variables and instances.

### To use the _converter_:
`from **unyts** import **convert**`  
`**convert**(_value_, *from_units*, *to_units*)`
where:
- _value_ is a number (int, float, numpy.array, etc)
- *from_units* is a string defining the units of _value_ (i.e.: 'ft')
- *to_units* is a string representing the units to convert _value_ (i.e.: 'km')

### To create instances of the _unit_ class using the _units_ function:
`from **unyts** import **units**`
`variable = **units**(_value_, _units_)`  
- _value_ is a number (`int`, `float`, `numpy.array`, etc)
- _units_ is a string defining the units of _value_ (i.e.: 'ft')

Then simply operate with the **Unit** instances or the variables related to them:  
 In: **units**(6, 'in') + **units**(1, 'ft')  
Out: 18_in  

### Referring to the `_Unit_` class:
`from **unyts** import **Unit**`
- Referring to `**Unit**` class is not intended to be used to create **Unit _instances_**, but to allow checking if other objects are instances of **Unit**: i.e.: `isinstance(variable, **Unit**)`
- In order to create instances of **Unit** it is convenient to use the **units** function as it will return the appropriate **Unit _subclass_**.

### Uses examples:
For further examples of use, the following Jupyter notebook <a href="https://github.com/ayaranitram/unyts/blob/master/unyts_demo.ipynb">**unyts_demo**</a> intends to be a guide on how to use this converter and units classes.

## To install this package:
Install it from the <a href="https://pypi.org/search/?q=unyts">pypi.org</a> repository:  
`pip install unyts`
or upgrade to the latest version:
`pip install --upgrade unyts`

## Optional requisites:
- `NumPy` to be able to deal with iterables not of nparray type, like (list of values) 
- `Pandas`
- `cloudpickle` to be able to save to cache file, for faster loading
- `openpyxl` if willing to export the units network to pandas DataFrame
