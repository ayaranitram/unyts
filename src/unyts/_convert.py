#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from ._database import unitsNetwork
from ._dictionaries import dictionary
from ._searches import BFS as _BFS, printPath as _printPath
from ._errors import NoConversionFound
import numpy as np
from functools import reduce

__version__ = '0.2.1'
__release__ = 20220822

#defaultPrintConversionPath = unitsNetwork.print  # True


def convertible(fromUnit, toUnit, PrintPath=False):
    try:
        if converter(1, fromUnit, toUnit, PrintPath) is not None:
            return True
        else:
            return False
    except:
        return False


def convertUnit(value, fromUnit, toUnit, PrintConversionPath=False):
    if type(PrintConversionPath) is not bool:
        if type(PrintConversionPath) in [int, float]:
            if PrintConversionPath > 1:
                PrintConversionPath = False
            else:
                PrintConversionPath = bool(PrintConversionPath)
        else:
            PrintConversionPath = True

    conv = converter(value, fromUnit, toUnit, PrintConversionPath)
    if conv is not None:
        return conv
    else:
        if PrintConversionPath:
            print(" No conversion found from '" + fromUnit + "' to '" + toUnit + "' .\n ... returning the received value for '" + str(fromUnit) + "'.")
        if type(value) is float and int(value) == value:
            value = int(value)
        return value


def convertUnit2(value, fromUnit, toUnit, PrintConversionPath=False):
    if type(PrintConversionPath) is not bool:
        if type(PrintConversionPath) in [int, float]:
            if PrintConversionPath > 1:
                PrintConversionPath = False
            else:
                PrintConversionPath = bool(PrintConversionPath)
        else:
            PrintConversionPath = True

    try:
        conv = converter2(value, fromUnit, toUnit, PrintConversionPath)
        if conv is not None:
            return conv
    except NoConversionFound:
        return None


def _applyConversion(value, conversionPath, PrintConversionPath=False):
    if PrintConversionPath:
        print( "\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + _printPath(conversionPath) )
    for conversion in range(len(conversionPath) - 1):
        value = unitsNetwork.convert(value, conversionPath[conversion], conversionPath[conversion + 1])
    return value


def _lambdaConversion(conversionPath, PrintConversionPath=False):
    if PrintConversionPath:
        print("\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + _printPath(conversionPath))
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


def _get_conversion(value, fromUnit, toUnit, PrintConversionPath=None, getPath=False):
    # specific cases for quick conversions
    ## no conversion required if 'from' and 'to' units are the same units
    if fromUnit == toUnit:
        return (lambda x: x) if value is None else value

    ## no conversion required if 'from' and 'to' units are dates
    if fromUnit in dictionary['date'] and toUnit in dictionary['date']:
        return (lambda x: x) if value is None else value

    ## dimensionless units does not require conversion
    if fromUnit.lower() in dictionary['dimensionless'] and toUnit.lower() in dictionary['dimensionless']:
        return (lambda x: x) if value is None else value

    ## from dimensionless to ratio of same units
    if fromUnit.lower() in dictionary['dimensionless'] and '/' in toUnit and len(toUnit.split('/')) == 2 and toUnit.lower().split('/')[0].strip(' ()') == toUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    ## from ratio of same units to dimensionless
    if toUnit.lower() in dictionary['dimensionless'] and '/' in fromUnit and len(fromUnit.split('/')) == 2 and fromUnit.lower().split('/')[0].strip(' ()') == fromUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    ## if inverted ratios
    if ('/' in fromUnit and len(fromUnit.split('/')) == 2) and ('/' in toUnit and len(toUnit.split('/')) == 2) and (fromUnit.split('/')[0].strip() == toUnit.split('/')[1].strip()) and (fromUnit.split('/')[1].strip() == toUnit.split('/')[0].strip()):
        return (lambda x: 1/x) if value is None else 1/value

    ## from dimensionless/None to some units or viceversa (to allow assign units to dimensionless numbers)
    if fromUnit is None or toUnit is None:
        return (lambda x: x) if value is None else value
    if fromUnit.lower() in dictionary['dimensionless'] or toUnit.lower() in dictionary['dimensionless']:
        return (lambda x: x) if value is None else value

    # check if already solved and memorized
    if not getPath and (fromUnit, toUnit) in unitsNetwork.Memory:
        conversionLambda = unitsNetwork.Memory[(fromUnit,toUnit)]
        return conversionLambda if value is None else conversionLambda(value)

    # check if path is alredy defined in network
    if unitsNetwork.hasNode(fromUnit) and unitsNetwork.hasNode(toUnit):
        conversionPath = _BFS(unitsNetwork, unitsNetwork.getNode(fromUnit), unitsNetwork.getNode(toUnit))
    else:
        conversionPath = None

    ## return conversion if found in network
    if conversionPath is not None:
        unitsNetwork.Memory[(fromUnit, toUnit)] = _lambdaConversion(conversionPath, PrintConversionPath=False)
        if getPath:
            return conversionPath
        return _applyConversion(value, conversionPath, PrintConversionPath) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)]


def converter2(value, fromUnit, toUnit, PrintConversionPath=None):
    """
    returns the received value (integer, float, array, series, dataframe, etc)
    transformed from the units 'fromUnit' to the units 'toUnits.
    """
    if hasattr(value, '__iter__') and type(value) is not np.array:
        value = np.array(value)

    PrintConversionPath = unitsNetwork.print if PrintConversionPath is None else bool(PrintConversionPath)

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
                                 PrintConversionPath=PrintConversionPath)

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
                                         PrintConversionPath=PrintConversionPath,
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
                raise NotImplemented("conversion from single to triple or more not implmented.")
            numerator = _get_conversion(1, fromNum, toNum, getPath=False)
            denominator = 1 / _get_conversion(1, fromDen, toDen, getPath=False)
            if numerator is not None and denominator is not None:
                conversionFactor = baseConversion * numerator / denominator
                unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x : x * conversionFactor
                return value * conversionFactor if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]

    # no conversion found
    raise NoConversionFound("from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")


def converter(value, fromUnit, toUnit, PrintConversionPath=None,
              AllowRecursion=unitsNetwork.RecursionLimit, Start=True):
    """
    returns the received value (integer, float, array, series, dataframe, etc)
    transformed from the units 'fromUnit' to the units 'toUnits.
    """

    if type(value) is list or type(value) is tuple:
        value = np.array(value)

    PrintConversionPath = unitsNetwork.print if PrintConversionPath is None else bool(PrintConversionPath)

    # strip off the parentesis, the string o
    if type(fromUnit) is str and fromUnit not in ('"',"'"):
        fromUnit = fromUnit.strip("( ')").strip('( ")').strip("'")
    else:
        fromUnit = fromUnit.strip("( )")
    if type(toUnit) is str and toUnit not in ('"',"'"):
        toUnit = toUnit.strip("( ')").strip('( ")').strip("'")
    else:
        toUnit = toUnit.strip("( )")

    # no conversion required if 'from' and 'to' units are the same units
    if fromUnit == toUnit:
        return (lambda x: x) if value is None else value

    # no conversion required if 'from' and 'to' units are dates
    if fromUnit in dictionary['date'] and toUnit in dictionary['date']:
        return (lambda x: x) if value is None else value

    # dimensionless units does not require conversion
    if fromUnit.lower() in dictionary['dimensionless'] and toUnit.lower() in dictionary['dimensionless']:
        return (lambda x: x) if value is None else value

    # from dimensionless to ratio of same units
    if fromUnit.lower() in dictionary['dimensionless'] and '/' in toUnit and len(toUnit.split('/')) == 2 and toUnit.lower().split('/')[0].strip(' ()') == toUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    # from ratio of same units to dimensionless
    if toUnit.lower() in dictionary['dimensionless'] and '/' in fromUnit and len(fromUnit.split('/')) == 2 and fromUnit.lower().split('/')[0].strip(' ()') == fromUnit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    # if inverted ratios
    if ('/' in fromUnit and len(fromUnit.split('/')) == 2) and ('/' in toUnit and len(toUnit.split('/')) == 2) and (fromUnit.split('/')[0].strip() == toUnit.split('/')[1].strip()) and (fromUnit.split('/')[1].strip() == toUnit.split('/')[0].strip()):
        return (lambda x: 1/x) if value is None else 1/value

    # reset memory for this variable
    if Start:
        unitsNetwork.previous = []

    # check if already solved and memorized
    if (fromUnit, toUnit) in unitsNetwork.Memory:
        conversionLambda = unitsNetwork.Memory[(fromUnit,toUnit)]
        return conversionLambda if value is None else conversionLambda(value)

    # check if path is alredy defined in network
    if unitsNetwork.hasNode(fromUnit) and unitsNetwork.hasNode(toUnit):
        conversionPath = _BFS(unitsNetwork, unitsNetwork.getNode(fromUnit), unitsNetwork.getNode(toUnit))
    else:
        conversionPath = None
    if conversionPath is not None:
        unitsNetwork.Memory[(fromUnit, toUnit)] = _lambdaConversion(conversionPath, PrintConversionPath=False)
        return _applyConversion(value, conversionPath, PrintConversionPath) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)]

    # check if pair from-to already visited
    if (fromUnit, toUnit) in unitsNetwork.previous:
        AllowRecursion = 0 # stop recursion here
    # append this pair to this search history
    unitsNetwork.previous.append((fromUnit, toUnit))


    if '/' in fromUnit and '*' not in fromUnit and len(fromUnit.split('/')) == 2 and '/' in toUnit and '*' not in toUnit and len(toUnit.split('/')) == 2:
        ### check for ratios of units, the simple case, from 'A/B' to 'C/D'
        # split numerator and denominator
        fromUp, fromDown = _splitRatio(fromUnit)
        toUp, toDown = _splitRatio(toUnit)

        # convert numerators, from 'A' to 'C'
        numerator = converter(None, fromUp, toUp, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if numerator is not None and (fromUp, toUp) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromUp, toUp)] = numerator
        # convert denominators, from 'B' to 'D'
        denominator = converter(None, fromDown, toDown, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if denominator is not None and (fromDown,toDown) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromDown, toDown)] = denominator

        # if both are not None, return the division
        if numerator is not None and denominator is not None:
            if (fromUnit, toUnit) not in unitsNetwork.Memory:
                unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x: numerator(x) / denominator(1)
            return unitsNetwork.Memory[(fromUnit, toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]

        ### try to convert the inverse, from 'B/A' to 'C/D'
        # convert numerators, from 'B' to 'C'
        numerator = converter(None, fromDown, toUp, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if numerator is not None and (fromDown,toUp) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromDown,toUp)] = numerator
        # convert denominators, from 'A' to 'D'
        denominator = converter(None, fromUp, toDown, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if denominator is not None and (fromUp, toDown) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromUp,toDown)] = denominator

        # if both are not None, return the inverse of the division
        if numerator is not None and denominator is not None:
            if (fromUnit, toUnit) not in unitsNetwork.Memory:
                unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x: denominator(1) / numerator(x)
            return unitsNetwork.Memory[(fromUnit, toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]


    if '*' in fromUnit and '/' not in fromUnit and len(fromUnit.split('*')) == 2 and '*' in toUnit and '/' not in toUnit and len(toUnit.split('*')) == 2:
        ### check for ratios of units, the simple case: from 'A*B' to 'C*D'
        # split Left and Right
        fromLeft, fromRight = _splitProduct(fromUnit)
        toLeft, toRight = _splitProduct(toUnit)

        # convert Left
        left = converter(None, fromLeft, toLeft, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if left is not None and (fromLeft,toLeft) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromLeft,toLeft)] = left
        # convert Right
        right = converter(None, fromRight, toRight, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
        if right is not None and (fromRight, toRight) not in unitsNetwork.Memory:
            unitsNetwork.Memory[(fromRight, toRight)] = right

        # if some is not None, try the other combination
        if left is None or right is None:
            # convert Left to Right
            left = converter(None, fromLeft, toRight, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
            if left is not None and (fromLeft,toRight) not in unitsNetwork.Memory:
                unitsNetwork.Memory[(fromLeft,toRight)] = left
            # convert Right to Left
            right = converter(None, fromRight, toLeft, PrintConversionPath=PrintConversionPath, AllowRecursion=AllowRecursion-1, Start=False)
            if right is not None and (fromRight,toLeft) not in unitsNetwork.Memory:
                unitsNetwork.Memory[(fromRight, toLeft)] = right

        # if both are not None, return the product
        if left is not None and right is not None:
            if (fromUnit, toUnit) not in unitsNetwork.Memory:
                unitsNetwork.Memory[(fromUnit, toUnit)] = lambda x: left(x) * right(1)
            return unitsNetwork.Memory[(fromUnit, toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit, toUnit)]

    return None