#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: martin
"""

from ._database import unitsNetwork
from ._dictionaries import dictionary
from ._searches import BFS as _BFS, printPath as _printPath
import numpy as np

def convertible(fromUnit, toUnit,PrintPath=False) :
    try :
        if converter(1,fromUnit,toUnit,PrintPath) != None :
            return True
        else :
            return False
    except :
        return False
    
    
def convertUnit(value, fromUnit, toUnit, PrintConversionPath=False ) :
    if type(PrintConversionPath) is not bool :
        if type(PrintConversionPath) in [ int , float ] :
            if PrintConversionPath > 1 :
                PrintConversionPath = False
            else :
                PrintConversionPath = bool( PrintConversionPath )
        else :
            PrintConversionPath = True
    
    conv = converter( value, fromUnit, toUnit, PrintConversionPath )
    if conv is not None :
        return conv
    else:
        if PrintConversionPath :
            print( " No conversion found from '" + fromUnit + "' to '" + toUnit + "' .\n ... returning the received value for '" + str(fromUnit) + "'." )
        if type(value) is float and int(value) == value :
            value = int(value)
        return value


def _applyConversion(value,conversionPath,PrintConversionPath=True) :
    if PrintConversionPath :
        # print( "\n converting from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")
        print( "\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + _printPath(conversionPath) )
    for conversion in range(len(conversionPath)-1) :
        value = unitsNetwork.convert(value,conversionPath[conversion],conversionPath[conversion+1])
    return value


def _lambdaConversion(conversionPath,PrintConversionPath=True) :
    if PrintConversionPath :
        # print( "\n converting from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")
        print( "\n converting from '" + str(conversionPath[0]) + "' to '" + str(conversionPath[-1]) + "'\n  " + _printPath(conversionPath) )
    bigLambda = []
    for i in range(len(conversionPath)-1) :
        bigLambda += [ unitsNetwork.conversion(conversionPath[i],conversionPath[i+1]) ]
    return lambda x : _lambdaLoop(x,bigLambda[:])


def _lambdaLoop(x,LambdaList) :
    for L in LambdaList :
        x=L(x)
    return x


def _splitRatio(unit) :
    unitUp , unitDown = unit.split('/')
    return unitUp.strip() , unitDown.strip()


def _splitProduct(unit) :
    unitA , unitB = unit.split('*')
    return unitA.strip() , unitB.strip()


def converter(value, fromUnit, toUnit, PrintConversionPath=None , AllowRecursion=unitsNetwork.RecursionLimit , Start=True) :
    """
    returns the received value (integer, float, array, series, dataframe, etc) 
    transformed from the units 'fromUnit' to the units 'toUnits.
    """
    
    if type(value) is list or type(value) is tuple :
        value = np.array(value)
    
    PrintConversionPath = unitsNetwork.print if PrintConversionPath is None else bool(PrintConversionPath)
    
    # strip off the parentesis, the string o
    if type(fromUnit) is str and fromUnit not in ('"',"'") :
        fromUnit = fromUnit.strip("( ')").strip('( ")').strip("'")
    else :
        fromUnit = fromUnit.strip("( )")
    if type(toUnit) is str and toUnit not in ('"',"'") :
        toUnit = toUnit.strip("( ')").strip('( ")').strip("'")
    else :
        toUnit = toUnit.strip("( )")
        
    # no conversion required if 'from' and 'to' units are the same units
    if fromUnit == toUnit :
        return (lambda x: x) if value is None else value
    
    # no conversion required if 'from' and 'to' units are dates
    if fromUnit in dictionary['date'] and toUnit in dictionary['date'] :
        return (lambda x: x) if value is None else value
    
    # dimensionless units does not require conversion
    if fromUnit.lower() in dictionary['dimensionless'] and toUnit.lower() in dictionary['dimensionless'] :
        return (lambda x: x) if value is None else value
    
    # from dimensionless to ratio of same units
    if fromUnit.lower() in dictionary['dimensionless'] and '/' in toUnit and len(toUnit.split('/'))==2 and toUnit.lower().split('/')[0].strip(' ()') == toUnit.lower().split('/')[1].strip(' ()')  :
        return (lambda x: x) if value is None else value
    
    # from ratio of same units to dimensionless
    if toUnit.lower() in dictionary['dimensionless'] and '/' in fromUnit and len(fromUnit.split('/'))==2 and fromUnit.lower().split('/')[0].strip(' ()') == fromUnit.lower().split('/')[1].strip(' ()')  :
        return (lambda x: x) if value is None else value
    
    # if inverted ratios
    if ( '/' in fromUnit and len(fromUnit.split('/'))==2 ) and ( '/' in toUnit and len(toUnit.split('/'))==2 ) and ( fromUnit.split('/')[0].strip() == toUnit.split('/')[1].strip() ) and ( fromUnit.split('/')[1].strip() == toUnit.split('/')[0].strip() ) :
        return (lambda x: 1/x) if value is None else 1/value
    
    # reset memory for this variable
    if Start :
        unitsNetwork.previous=[]
        
    # check if already solved and memorized
    if (fromUnit,toUnit) in unitsNetwork.Memory :
        # conversionPath = unitsNetwork.Memory[(fromUnit,toUnit)]
        # return _applyConversion(value, conversionPath, PrintConversionPath) if value is not None else _lambdaConversion(fromUnit,toUnit)
        conversionLambda = unitsNetwork.Memory[(fromUnit,toUnit)]
        return conversionLambda if value is None else conversionLambda(value)
    
    # check if path is alredy defined in network
    if unitsNetwork.hasNode(fromUnit) and unitsNetwork.hasNode(toUnit) :
        conversionPath = _BFS( unitsNetwork, unitsNetwork.getNode(fromUnit), unitsNetwork.getNode(toUnit) )
    else :
        conversionPath = None
    if conversionPath is not None :
        unitsNetwork.Memory[(fromUnit,toUnit)] = _lambdaConversion(conversionPath,PrintConversionPath=False) 
        return _applyConversion(value, conversionPath, PrintConversionPath) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)]
    
    # check if pair from-to already visited
    if (fromUnit,toUnit) in unitsNetwork.previous :
        AllowRecursion = 0 # stop recursion here
    # append this pair to this search history
    unitsNetwork.previous.append((fromUnit,toUnit))
    
    
    if '/' in fromUnit and '*' not in fromUnit and len(fromUnit.split('/'))==2 and '/' in toUnit and '*' not in toUnit and len(toUnit.split('/'))==2 :
        ### check for ratios of units, the simple case, from 'A/B' to 'C/D'
        # split numerator and denominator
        fromUp , fromDown = _splitRatio(fromUnit)
        toUp , toDown = _splitRatio(toUnit)
        
        # convert numerators, from 'A' to 'C'
        numerator = converter(None,fromUp,toUp , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if numerator is not None and (fromUp,toUp) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromUp,toUp)] = numerator
        # convert denominators, from 'B' to 'D'
        denominator = converter(None,fromDown,toDown , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if denominator is not None and (fromDown,toDown) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromDown,toDown)] = denominator
            
        # if both are not None, return the division
        if numerator is not None and denominator is not None :
            if (fromUnit,toUnit) not in unitsNetwork.Memory :
                unitsNetwork.Memory[(fromUnit,toUnit)] = lambda x : numerator(x) / denominator(1)
            return unitsNetwork.Memory[(fromUnit,toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)] 
        
        ### try to convert the inverse, from 'B/A' to 'C/D'
        # convert numerators, from 'B' to 'C'
        numerator = converter(None,fromDown,toUp , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if numerator is not None and (fromDown,toUp) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromDown,toUp)] = numerator
        # convert denominators, from 'A' to 'D'
        denominator = converter(None,fromUp,toDown , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if denominator is not None and (fromUp,toDown) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromUp,toDown)] = denominator
            
        # if both are not None, return the inverse of the division
        if numerator is not None and denominator is not None :
            if (fromUnit,toUnit) not in unitsNetwork.Memory :
                unitsNetwork.Memory[(fromUnit,toUnit)] = lambda x : denominator(1) / numerator(x)
            return unitsNetwork.Memory[(fromUnit,toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)] 
        
        
    if '*' in fromUnit and '/' not in fromUnit and len(fromUnit.split('*'))==2 and '*' in toUnit and '/' not in toUnit and len(toUnit.split('*'))==2 :
        ### check for ratios of units, the simple case: from 'A*B' to 'C*D'
        # split Left and Right
        fromLeft , fromRight = _splitProduct(fromUnit)
        toLeft , toRight = _splitProduct(toUnit)
        
        # convert Left
        left = converter(None,fromLeft,toLeft , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if left is not None and (fromLeft,toLeft) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromLeft,toLeft)] = left
        # convert Right
        right = converter(None,fromRight,toRight , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
        if right is not None and (fromRight,toRight) not in unitsNetwork.Memory :
            unitsNetwork.Memory[(fromRight,toRight)] = right
            
        # if some is not None, try the other combination
        if left is None or right is None :
            # convert Left to Right
            left = converter(None,fromLeft,toRight , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
            if left is not None and (fromLeft,toRight) not in unitsNetwork.Memory :
                unitsNetwork.Memory[(fromLeft,toRight)] = left
            # convert Right to Left
            right = converter(None,fromRight,toLeft , PrintConversionPath=PrintConversionPath , AllowRecursion=AllowRecursion-1 , Start=False)
            if right is not None and (fromRight,toLeft) not in unitsNetwork.Memory :
                unitsNetwork.Memory[(fromRight,toLeft)] = right
            
        # if both are not None, return the product
        if left is not None and right is not None :
            if (fromUnit,toUnit) not in unitsNetwork.Memory :
                unitsNetwork.Memory[(fromUnit,toUnit)] = lambda x : left(x) * right(1)
            return unitsNetwork.Memory[(fromUnit,toUnit)](value) if value is not None else unitsNetwork.Memory[(fromUnit,toUnit)] 
        
    return None

    
    # # if PrintConversionPath :
    # #     print( "\n converting from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")
    
    # # if converting from or to any dimensionless units, 
    # # the other unit has to have the same in numerator and denominator 
    # for pair in ((fromUnit,toUnit),(toUnit,fromUnit)) :
    #     if pair[0].lower().strip(' ()') in dictionary['dimensionless'] :
    #         if pair[1].lower().strip(' ()') not in dictionary['dimensionless'] :
    #             if '/' in pair[1] :
    #                 if pair[1].split('/')[0] == pair[1].split('/')[1] :
    #                     return value
    #                 else :
    #                     unitsNetwork.previous=(fromUnit,toUnit)
    #                     if ( pair[1].split('/')[0] , pair[1].split('/')[1] ) in unitsNetwork.Memory :
    #                         conv = unitsNetwork.Memory[ ( pair[1].split('/')[0] , pair[1].split('/')[1] ) ]
    #                     else :
    #                         conv = converter( 1 , pair[1].split('/')[0] , pair[1].split('/')[1] , AllowRecursion , Start=False )
    #                         unitsNetwork.Memory[ ( pair[1].split('/')[0] , pair[1].split('/')[1] ) ] = conv
    #                     if type(conv) != None:
    #                         return value / conv
                        
    # if (fromUnit,toUnit) in unitsNetwork.previous :
    #     AllowRecursion = 0
    # unitsNetwork.previous.append((fromUnit,toUnit))
    # # try to found conversion path for the input parameters un the defined graph:
    # try :
    #     conversionPath = _BFS(unitsNetwork, unitsNetwork.getNode(fromUnit), unitsNetwork.getNode(toUnit) )
    # except : # if the units doesn't exists the _BFS function returns error
    #     conversionPath = None
    
    # # if direct conversion fail, try to divide the unit to it fundamental units
    # if conversionPath == None and AllowRecursion > 0 :
    #     # print( 'doing something... /')
    #     operator = ''
    #     if fromUnit == toUnit or ( fromUnit in dictionary['date'] and toUnit in dictionary['date'] ) :
    #         partA = fromUnit
    #         partB = toUnit
    #         operator = ' = '
    #     # print(fromUnit,toUnit )
    #     if conversionPath == None and ( '/' in fromUnit or '/' in toUnit ) :
    #         AllowRecursion -= 1
    #         if '/' in fromUnit and '/' in toUnit :
    #             operator = ' / '
    #             if ( fromUnit.split('/')[0] , toUnit.split('/')[0] ) in unitsNetwork.Memory :
    #                 partA = value * unitsNetwork.Memory[ ( fromUnit.split('/')[0] , toUnit.split('/')[0] ) ] # numerator
    #             else :
    #                 partA = converter(  1 , fromUnit.split('/')[0] , toUnit.split('/')[0] , PrintConversionPath , AllowRecursion , Start=False ) # numerator
    #                 unitsNetwork.Memory[ ( fromUnit.split('/')[0] , toUnit.split('/')[0] ) ] = partA
    #                 PartA = value * unitsNetwork.Memory[ ( fromUnit.split('/')[0] , toUnit.split('/')[0] ) ]
    #             if ( fromUnit.split('/')[1] , toUnit.split('/')[1] ) in unitsNetwork.Memory :
    #                 partB = unitsNetwork.Memory[ ( fromUnit.split('/')[1] , toUnit.split('/')[1] ) ] 
    #             else :
    #                 partB = converter(    1 , fromUnit.split('/')[1] , toUnit.split('/')[1] , PrintConversionPath , AllowRecursion , Start=False ) # denominator
    #                 unitsNetwork.Memory[ ( fromUnit.split('/')[1] , toUnit.split('/')[1] ) ]  = partB
    #             if type(partA) == None or type(partB) == None :
    #                 # if PrintConversionPath :
    #                 # print( "no conversion found from " + fromUnit + " to " + toUnit + " ." )
    #                 # conversionPath = None 
    #                 for middleFrom in unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit)) : #+ unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit.split('/')[0])) + unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit.split('/')[1])) :
    #                     #for middleTo in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) : # + unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit.split('/')[0])) + unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit.split('/')[1])) :
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , Start=False ) , str(middleFrom) , toUnit , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return middle
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , Start=False ) , str(middleFrom) , toUnit.split('/')[0] , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return middle 
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , Start=False ) , str(middleFrom) , toUnit.split('/')[1] , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return 1/middle
    #                 for middleTo in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) :
    #                     middle = converter( value , fromUnit , str(middleTo) , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return converter( middle , str(middleTo) , toUnit, PrintConversionPath , AllowRecursion , Start=False )

    #                 # return value
    #             else :
    #                 # if returnPath :
    #                 #     return ( partA , operator , partB)
    #                 # else:
    #                 return partA / partB
    #         elif '/' in fromUnit :
    #             # print('if / in fromUnit')
    #             for middleUnit in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) :
    #                 # print('from ' + fromUnit + ' to ' + str(middleUnit))
    #                 middle = converter(value, fromUnit , str(middleUnit), PrintConversionPath , AllowRecursion , Start=False )
    #                 if type(middle) != None :
    #                     return converter(middle, str(middleUnit), toUnit, PrintConversionPath , AllowRecursion , Start=False )  

    #         else : # elif '/' in toUnit :
    #             # print('if / in toUnit ')
    #             for middleUnit in unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit)) :
    #                 # print('from ' + fromUnit + ' to ' + str(middleUnit))
    #                 middle = converter( converter( value , fromUnit , str(middleUnit) , PrintConversionPath ) , str(middleUnit), toUnit, PrintConversionPath , AllowRecursion , Start=False )
    #                 if type(middle) != None :
    #                     return middle
    #         return None

                
    # # if direct conversion fail, try to multiply the unit to it fundamental units
    # if conversionPath == None and AllowRecursion > 0 :
    #     # print( 'doing something... *')
    #     operator = ''
    #     if fromUnit == toUnit or ( fromUnit in dictionary['date'] and toUnit in dictionary['date'] ) :
    #         partA = fromUnit
    #         partB = toUnit
    #         operator = ' = '
        
    #     if conversionPath == None and ( '*' in fromUnit or '*' in toUnit ) :
    #         AllowRecursion -= 1
    #         if '*' in fromUnit and '*' in toUnit :
    #             operator = ' * '
    #             partA = converter(value , fromUnit.split('*')[0] , toUnit.split('*')[0] , PrintConversionPath , AllowRecursion , Start=False ) # 1st factor
    #             partB = converter(    1 , fromUnit.split('*')[1] , toUnit.split('*')[1] , PrintConversionPath , AllowRecursion , Start=False ) # 2nd factor
    #             if type(partA) == None or type(partB) == None :
    #                 # if PrintConversionPath :
    #                 # print( "no conversion found from " + fromUnit + " to " + toUnit + " ." )
    #                 # conversionPath = None 
    #                 for middleFrom in unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit)) : #+ unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit.split('/')[0])) + unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit.split('/')[1])) :
    #                     #for middleTo in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) : # + unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit.split('/')[0])) + unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit.split('/')[1])) :
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , AllowRecursion, Start=False ) , str(middleFrom) , toUnit , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return middle
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , AllowRecursion, Start=False ) , str(middleFrom) , toUnit.split('/')[0] , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return middle 
    #                     middle = converter( converter( value , fromUnit , str(middleFrom) , PrintConversionPath , AllowRecursion, Start=False ) , str(middleFrom) , toUnit.split('/')[1] , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return 1/middle
    #                 for middleTo in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) :
    #                     middle = converter( value , fromUnit , str(middleTo) , PrintConversionPath , AllowRecursion , Start=False )
    #                     if type(middle) != None :
    #                         return converter( middle , str(middleTo) , toUnit, PrintConversionPath , AllowRecursion, Start=False )
                        
    #                 # return value
    #             else :
    #                 # if returnPath :
    #                 #     return ( partA , operator , partB)
    #                 # else:
    #                 return partA * partB
    #         elif '*' in fromUnit :
    #             # print('if * in fromUnit')
    #             for middleUnit in unitsNetwork.childrenOf(unitsNetwork.getNode(toUnit)) :
    #                 # print('from ' + fromUnit + ' to ' + str(middleUnit))
    #                 middle = converter(value, fromUnit , str(middleUnit), PrintConversionPath , AllowRecursion , Start=False )
    #                 if type(middle) != None :
    #                     return converter(middle, str(middleUnit), toUnit, PrintConversionPath , AllowRecursion, Start=False )  

    #         else : # elif '*' in toUnit :
    #             # print('if * in toUnit ')
    #             for middleUnit in unitsNetwork.childrenOf(unitsNetwork.getNode(fromUnit)) :
    #                 # print('from ' + fromUnit + ' to ' + str(middleUnit))
    #                 middle = converter( converter( value , fromUnit , str(middleUnit) , PrintConversionPath , AllowRecursion, Start=False ) , str(middleUnit), toUnit, PrintConversionPath , AllowRecursion , Start=False )
    #                 if type(middle) != None :
    #                     return middle 
    #         return None
            

    # if conversionPath == None :
    #     # if PrintConversionPath :
    #     # print( "no conversion found from " + fromUnit + " to " + toUnit + " ." )
    #     return None

    # # if returnPath :
    # #     return conversionPath

    # if type(value) == list or type(value) == tuple :
    #     value = np.array(value)
    # if PrintConversionPath == True and conversionPath != None:
    #     # print( "\n converting from '" + str(fromUnit) + "' to '" + str(toUnit) + "'")
    #     print( "\n converting from '" + str(fromUnit) + "' to '" + str(toUnit) + "'\n  " + _printPath(conversionPath) )
    # for conversion in range(len(conversionPath)-1) :
    #     value = unitsNetwork.convert(value,conversionPath[conversion],conversionPath[conversion+1])
    # # if type(value) == float and int(value) == value :
    # #     value = int(value)
    
    # return value
