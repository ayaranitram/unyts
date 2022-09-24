#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.2'
__release__ = 20220924
__all__ = ['converter', 'convertible', 'convertUnit']


from .database import unitsNetwork
from .dictionaries import dictionary, temperatureRatioConversions
from .searches import BFS, printPath
from .errors import NoConversionFoundError
import numpy as np
from functools import reduce


def _cleanPrintConversionPath(printConversionPath):
    if printConversionPath is None:
        printConversionPath = unitsNetwork.print
    elif type(printConversionPath) is not bool:
        if type(printConversionPath) in [int, float]:
            if printConversionPath == 1:
                printConversionPath = True
            else:
                printConversionPath = False
        else:
            printConversionPath = True
    return printConversionPath


def convertible(fromUnit, toUnit, PrintPath=False):
    try:
        converter(1, fromUnit, toUnit, False)
        return True
    except:
        return False


def convertUnit(value, fromUnit, toUnit, printConversionPath=False):
    """
    returns the received value (integer, float, array, Series, DataFrame, etc)
    transformed from the units 'fromUnit' to the units 'toUnits.

    Parameters
    ----------
    value : int, float, array, Series, DataFrame, etc
        the value to be converted.
    fromUnit : str
        the units of the provided value.
    toUnit : str
        the units to convert the value.
    printConversionPath : bool, optional
        Set to True to show the path used for conversion. The default is False.

    Returns
    -------
    converted_value : int, float, array, Series, DataFrame ...
        the converted value

    """
    printConversionPath = _cleanPrintConversionPath(printConversionPath)

    try:
        conv = converter(value, fromUnit, toUnit, printConversionPath)
        if conv is not None:
            return conv
    except NoConversionFoundError:
        return None


def convertUnit_for_SimPandas(value, fromUnit, toUnit, printConversionPath=False):
    printConversionPath = _cleanPrintConversionPath(printConversionPath)

    try:
        conv = converter(value, fromUnit, toUnit, printConversionPath)
        if conv is not None:
            return conv
        else:
            return value
    except NoConversionFoundError:
        return value


def _applyConversion(value, conversionPath, printConversionPath=False):
    if printConversionPath:
        print( "\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + printPath(conversionPath) )
    for conversion in range(len(conversionPath) - 1):
        value = unitsNetwork.convert(value, conversionPath[conversion], conversionPath[conversion + 1])
    return value


def _lambdaConversion(conversionPath, printConversionPath=False):
    if printConversionPath:
        print("\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + printPath(conversionPath))
    bigLambda = []
    for i in range(len(conversionPath) - 1):
        bigLambda += [unitsNetwork.conversion(conversionPath[i],conversionPath[i + 1])]
    return lambda x: _lambdaLoop(x, bigLambda[:])


def _lambdaLoop(x, LambdaList):
    for L in LambdaList:
        x=L(x)
    return x


def _splitRatio(unit):
    unitUp , unitDown = unit.split('/')
    return unitUp.strip(), unitDown.strip()


def _splitProduct(unit):
    unitA , unitB = unit.split('*')
    return unitA.strip(), unitB.strip()


def _splitUnit(unit):
    result = None
    for c in unit:
        if c in '*/':
            result.append(c)
        elif result is None:
            result = [c]
        elif result[-1] in '*/':
            result.append(c)
        else:
            result[-1] = result[-1] + c
    return result


def _getPairChild(unit):

    # get the unit node if the name received
    unit = unitsNetwork.getNode(unit) if type(unit) is str else unit

    # get pair of units children
    pairChild = list(filter(lambda u: '/' in u or '*' in u, [u.getName() for u in unitsNetwork.childrenOf(unit)]))

    ## if pair of units child is found, return the one with the shorter name
    if len(pairChild) > 0:
        pairChild = sorted(pairChild, key=len)[0]

    ## if no children found at this level, look for children in next level
    else:
        for child in unitsNetwork.childrenOf(unit):
            pairGrandchild = list(filter(lambda u: '/' in u or '*' in u, [u.getName() for u in unitsNetwork.childrenOf(child)]))
            if len(pairGrandchild) > 0:
                pairChild = sorted(pairGrandchild, key=len)[0]
                break

    if type(pairChild) is str:
        return pairChild


def _get_conversion(value, fromUnit, toUnit, printConversionPath=None, getPath=False):
    # specific cases for quick conversions
    ## no conversion required if 'from' and 'to' units are the same units
    if fromUnit == toUnit:
        return (lambda x: x) if value is None else value

    ## no conversion required if 'from' and 'to' units are dates
    if fromUnit in dictionary['date'] and toUnit in dictionary['date']:
        return (lambda x: x) if value is None else value

    ## special case for temperature ratios
    if '/' in fromUnit and len(fromUnit.split('/'))==2 and fromUnit.split('/')[0] in dictionary['temperature'] \
        and '/' in toUnit and len(toUnit.split('/'))==2 and toUnit.split('/')[0] in dictionary['temperature']:
            t1, d1 = fromUnit.split('/')
            t2, d2 = toUnit.split('/')
            num = temperatureRatioConversions[(t1, t2)]
            den = _get_conversion(1, d1, d2, printConversionPath=printConversionPath, getPath=getPath)
            if num is None or den is None:
                return None  # raise NoConversionFound("from '" + str(d1) + "' to '" + str(d2) + "'")
            return (lambda x: x * num / den) if value is None else (value * num / den)

    ## from dimensionless/None to some units or viceversa (to allow assign units to dimensionless numbers)
    if fromUnit is None or toUnit is None:
        return (lambda x: x) if value is None else value
    if (fromUnit.lower() in dictionary['dimensionless'] or toUnit.lower() in dictionary['dimensionless']) and (fromUnit is None or toUnit is None):
        return (lambda x: x) if value is None else value

    ## from dimensionless to percentage or viceversa
    if (fromUnit is None or fromUnit.lower() in dictionary['dimensionless']) and toUnit.lower() in dictionary['percentage']:
        return (lambda x: x * 100) if value is None else value * 100
    if fromUnit.lower() in dictionary['percentage'] and (toUnit is None or toUnit.lower() in dictionary['dimensionless']):
        return (lambda x: x / 100) if value is None else value / 100

    ## from dimensionless to ratio of same units
    if fromUnit.lower() in dictionary['dimensionless'] and '/' in toUnit and len(toUnit.split('/')) == 2 and toUnit.lower().split('/')[0].strip(' ()') == toUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    ## from ratio of same units to dimensionless
    if toUnit.lower() in dictionary['dimensionless'] and '/' in fromUnit and len(fromUnit.split('/')) == 2 and fromUnit.lower().split('/')[0].strip(' ()') == fromUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    ## if inverted ratios
    if ('/' in fromUnit and len(fromUnit.split('/')) == 2) and ('/' in toUnit and len(toUnit.split('/')) == 2) and (fromUnit.split('/')[0].strip() == toUnit.split('/')[1].strip()) and (fromUnit.split('/')[1].strip() == toUnit.split('/')[0].strip()):
        return (lambda x: 1/x) if value is None else 1/value

    # check if already solved and memorized
    if not getPath and (fromUnit, toUnit) in unitsNetwork.Memory:
        conversionLambda = unitsNetwork.Memory[(fromUnit,toUnit)]
        return conversionLambda if value is None else conversionLambda(value)

    # check if path is alredy defined in network
    if unitsNetwork.hasNode(fromUnit) and unitsNetwork.hasNode(toUnit):
        conversionPath = BFS(unitsNetwork, unitsNetwork.getNode(fromUnit), unitsNetwork.getNode(toUnit))
    else:
        conversionPath = None

    ## return conversion if found in network
    if conversionPath is not None:
        unitsNetwork.Memory[(fromUnit, toUnit)] = _lambdaConversion(conversionPath, printConversionPath=False)
        if getPath:
            return conversionPath
        return _applyConversion(value, conversionPath, printConversionPath) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)]


def converter(value, fromUnit, toUnit, printConversionPath=None):
    """
    returns the received value (integer, float, array, series, dataframe, etc)
    transformed from the units 'fromUnit' to the units 'toUnits.
    """
    if hasattr(value, '__iter__') and type(value) is not np.array:
        value = np.array(value)

    printConversionPath = _cleanPrintConversionPath(printConversionPath)

    # cleaning inputs
    ## strip off the parentesis, the string o
    if type(fromUnit) is str and fromUnit not in ('"',"'"):
        fromUnit = fromUnit.strip("( ')").strip('( ")').strip("'")
    else:
        fromUnit = fromUnit.strip("( )")
    if type(toUnit) is str and toUnit not in ('"',"'"):
        toUnit = toUnit.strip("( ')").strip('( ")').strip("'")
    else:
        toUnit = toUnit.strip("( )")

    # reset memory for this variable
    unitsNetwork.previous = []

    # try to convert
    conversion = _get_conversion(value, fromUnit, toUnit,
                                 printConversionPath=printConversionPath)

    ## if convertion found
    if conversion is not None:
        return conversion

    # else, if conversion path not found, start a new search part by part
    ## check if pair from-to already visited
    if (fromUnit, toUnit) in unitsNetwork.previous:
        AllowRecursion = 0  # stop recursion here
    ## append this pair to this search history
    unitsNetwork.previous.append((fromUnit, toUnit))

    listConversion = []
    splitFrom = _splitUnit(fromUnit)
    splitTo = _splitUnit(toUnit)
    usedTo = []
    failed = False
    for f in range(len(splitFrom)):
        flag = False
        if splitFrom[f] in '*/':
            continue
        for t in range(len(splitTo)):
            if t in usedTo:
                continue
            if splitTo[t] in '*/':
                continue
            conversion = _get_conversion(1, splitFrom[f], splitTo[t],
                                         printConversionPath=printConversionPath,
                                         getPath=False)
            if conversion is not None:
                flag = True
                if (f > 0 and splitFrom[f-1] == '/') or (t > 0 and splitTo[t-1] == '/'):
                    conversion = 1 / conversion
                listConversion.append(conversion)
                usedTo.append(t)
                break
        if not flag:
            failed = True
            break

    if listConversion != [] and not failed:
        conversionFactor = reduce(lambda x, y : x * y, listConversion)
        unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x : x * conversionFactor
        return value * conversionFactor if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]

    # look for one to pair conversion
    if ('/' in toUnit or '*' in toUnit) and ('/' not in fromUnit and '*' not in fromUnit):
        fromUnitChild = _getPairChild(fromUnit)
        if fromUnitChild is not None:
            baseConversion = _get_conversion(1, fromUnit, fromUnitChild)
            sep = '/' if '/' in fromUnitChild else '*'
            fromNum, fromDen = fromUnitChild.split(sep)
            sep = '/' if '/' in toUnit else '*'
            if len(toUnit.split(sep)) == 2:
                toNum, toDen = toUnit.split(sep)
            else:
                raise NotImplementedError("conversion from single to triple or more not implmented.")
            numerator = _get_conversion(1, fromNum, toNum, getPath=False)
            denominator = 1 / _get_conversion(1, fromDen, toDen, getPath=False)
            if numerator is not None and denominator is not None:
                conversionFactor = baseConversion * numerator / denominator
                unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x : x * conversionFactor
                return value * conversionFactor if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]

    # no conversion found
    raise NoConversionFoundError("from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")