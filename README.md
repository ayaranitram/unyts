# unyts
After culminating a project for a class from MITx courses, I saw the opportunity to use a *digraph network* to build a unit converter able to convert from any units to any units without the need to populate a huge but finite table of possible conversions. Powered by the _Breadth First Search_, or _BFS_, algorithm to search through the network, this converter can find conversions from a particular unit (or ratio of units) to any other unit (or ratio) as long as a path connecting them exists.

This package is under development and is regularly updated. Back compatibility is intended to be maintained when possible.

## What Contains This Package
- It is loaded with the network of units preloaded for distances, area, volume, mass and time conversions defined for SI and Imperial systems according to the definition of each unit, i.e.: _1_foot = 12_inches_.
- Prefixes applied to the basic units, like _k_ to _m_ to make _km_, are loaded as a network of conversion paths allowing the algorithm to apply the prefix to any other unit on the same system.
- It provides classes of _unit_ useful powered with arithmetic and logic operations to intrinsically consider unit conversions when making calculations.

## How To Use It
To install it from the PyPI repository:  
**pip install unyts**

### To use the _converter_:
from **unyts** import **convert**  
**convert**(_value_, _sourceUnits_, _unitsToConvertTo_)
where:
- _value_ is a number (int, float, numpy.array, etc)
- _sourceUnits_ is a string defining the units of _value_ (i.e.: 'ft')
- _unitsToConvertTo_ is a string representing the units to convert _value_ (i.e.: 'km')

### To refer to the _unit_ class:
from **unyts** import **unit**
- refering to **unit** class is not intended to be used to create **unit _instances_**, but to allow checking if other objects are instances of **unit**: i.e.: isinstance(variable, **unit**)
- in order to create instances of **unit** it is convenient to use the **units** function as it will return the appropriate **unit _subclass_**.

### To create instances of the _unit_ class using the _units_ function:
from **unyts** import **units**  
variable = **units**(_value_, _units_)  
- _value_ is a number (int, float, numpy.array, etc)
- _units_ is a string defining the units of _value_ (i.e.: 'ft')

Then simply operate with the **unit** instances or the variables related to them:  
 In: **units**(6, 'in') + **units**(1, 'ft')  
Out: 18_in  

#### For further examples:
The Jupyter notebook **unyts_demo** intends to be a guide on how to use this converter and units classes.

## Requisites
- NumPy

## To install this package:
pip install unyts
