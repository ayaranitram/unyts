#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:36:48 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__all__ = ['unitsNetwork']
__version__ = '0.2.6'
__release__ = 20220831

from ._dictionaries import SI, SI_order, OGF, OGF_order, DATA, DATA_order, dictionary, StandardAirDensity, StandadEarthGravity


class uNode(object):
    def __init__(self,name):
        self.name = name if type(name) is str else ''
    def getName(self):
        return self.name
    def __str__(self):
        return self.name


class uDigraph(object):
    """edges is a dict mapping each node to a list of its children"""
    def __init__(self):
        self.edges = {}
        self.previous=[(None, None)]
        self.RecursionLimit = 5
        self.fvf = None
        self.Memory = {}
        self.fvf = None
        self.print = False

    def addNode(self, node):
        if node in self.edges:
            raise ValueError('Duplicate node')
        else:
            self.edges[node] = [], []

    def addEdge(self, edge, reverse=False):
        src = edge.getSource()
        dest = edge.getDestination()
        conv = edge.getConvert()
        if not (src in self.edges and dest in self.edges):
            raise ValueError('Node not in graph')
        self.edges[src][0].append(dest)
        self.edges[src][1].append(conv)

    def childrenOf(self, node):
        return self.edges[node][0]

    def hasNode(self, node):
        if type(node) is str:
            return node in [n.getName() for n in self.edges]
        else:
            return node in self.edges

    def getNode(self, name):
        for n in self.edges:
            if n.getName() == name:
                return n
        raise NameError(name)

    def listNodes(self):
        return list(set([N.getName() for N in self.edge.keys()]))

    def convert(self,value,src,dest):
        if type(src) != uNode:
            src = self.getNode(src)
        if type(dest) != uNode:
            dest = self.getNode(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)](value)

    def conversion(self,src,dest):
        if type(src) != uNode:
            src = self.getNode(src)
        if type(dest) != uNode:
            dest = self.getNode(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)]

    def __str__(self):
        result = ''
        for src in self.edges:
            for dest in self.edges[src]:
                result = result + src.getName() + '->'\
                         + dest.getName() +\
                         str(self.conv) + '\n'
        return result[:-1]  # remove final newline

    def set_fvf(self, FVF):
        if type(FVF) is str:
            try:
                FVF = float(FVF)
            except:
                print('received FVF value is not a number: ' + str(FVF))
        if type(FVF) in [int, float]:
            if FVF <= 0:
                print('FVF should be a positive number...')
            self.fvf = FVF

    def get_fvf(self):
        def valid_fvf(FVF):
            if type(FVF) is str:
                try:
                    FVF = float(FVF)
                except:
                    return False
            if type(FVF) is int or type(FVF) is float:
                if FVF <= 0:
                    return False
                else:
                    return FVF
            return False

        if self.fvf is None:
            print('Please enter formation volume factor (FVF) in reservoir_volume/standard_volume:')
            while self.fvf is None:
                self.fvf = input(' FVF (rV/stV) = ')
                if not self.valid_fvf(self.fvf):
                    self.fvf = None
                else:
                    self.fvf = self.valid_fvf(self.fvf)
        return self.fvf


class conversion(object):
    def __init__(self, src, dest, conv, reverse=False):
        """Assumes src and dest are nodes"""
        self.src = src
        self.dest = dest
        self.conv = conv
        self.rev = reverse
    def getSource(self):
        return self.src
    def getDestination(self):
        return self.dest
    def convert(self,value):
        return self.conv(value)
    def reverse(self,value):
        return value/self.conv(1)
    def getConvert(self):
        if self.rev and self.conv is not None:
            return lambda X: X/self.conv(1)
        else:
            return self.conv
    def __str__(self):
        return self.src.getName() + '->' + self.dest.getName()


def _loadNetwork():
    network = uDigraph()

    for unitKind in list(dictionary.keys()):
        # print('1: ' +unitKind)
        if '_' not in unitKind :
            for unitName in dictionary[unitKind]:
                # print('_ 2: ' + unitName)
                network.addNode(uNode(unitName))
        if '_NAMES' in unitKind:
            for unitName in list(dictionary[unitKind].keys()):
                # print('N  2: ' + unitName,unitKind.split('_')[0])
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for secondName in dictionary[unitKind][unitName]:
                    # print('N   3: ' + unitName)
                    network.addNode(uNode(secondName))
                    network.addEdge(conversion(network.getNode(secondName), network.getNode(unitName), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(secondName), lambda X: X))
                    dictionary[unitKind.split('_')[0]].append(secondName)
                # for secondName in dictionary[unitKind][unitName]:
                #     for t in range(dictionary[unitKind][unitName].index(secondName)+1, len(dictionary[unitKind][unitName])):
                #         thirdName = dictionary[unitKind][unitName][t]
                #         network.addEdge(conversion(network.getNode(secondName), network.getNode(thirdName), lambda X: X))
                #         network.addEdge(conversion(network.getNode(thirdName), network.getNode(secondName), lambda X: X))
                    

        if '_SPACES' in unitKind:
            for unitName in list(dictionary[unitKind].keys()):
                # print('N  2: ' + unitName,unitKind.split('_')[0])
                if ' ' in unitName:
                    network.addNode(uNode(unitName))
                    network.addNode(uNode(unitName.replace(' ', '-')))
                    dictionary[unitKind.split('_')[0]].append(unitName)
                    dictionary[unitKind.split('_')[0]].append(unitName.replace(' ', '-'))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.replace(' ', '-')), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.replace(' ', '-')), lambda X: X))
                    for secondName in dictionary[unitKind][unitName]:
                        # print('N   3: ' + unitName)
                        if ' ' in secondName:
                            network.addNode(uNode(secondName))
                            network.addNode(uNode(secondName.replace(' ', '-')))
                            network.addEdge(conversion(network.getNode(secondName.replace(' ', '-')), network.getNode(secondName), lambda X: X))
                            network.addEdge(conversion(network.getNode(secondName), network.getNode(secondName.replace(' ', '-')), lambda X: X))
                            dictionary[unitKind.split('_')[0]].append(secondName)
                            dictionary[unitKind.split('_')[0]].append(secondName.replace(' ', '-'))
                else:
                    for secondName in dictionary[unitKind][unitName]:
                        # print('N   3: ' + unitName)
                        if ' ' in secondName:
                            network.addNode(uNode(secondName))
                            network.addNode(uNode(secondName.replace(' ', '-')))
                            network.addEdge(conversion(network.getNode(secondName.replace(' ', '-')), network.getNode(secondName), lambda X: X))
                            network.addEdge(conversion(network.getNode(secondName), network.getNode(secondName.replace(' ', '-')), lambda X: X))
                            dictionary[unitKind.split('_')[0]].append(secondName)
                            dictionary[unitKind.split('_')[0]].append(secondName.replace(' ', '-'))

        if '_SI' in unitKind and unitKind.split('_')[0] in SI_order[0]:
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix][0]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), SI[prefix][0]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), SI[prefix][0], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_SI' in unitKind and unitKind.split('_')[0]  in SI_order[1]:
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix][1]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), SI[prefix][1]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), SI[prefix][1], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_SI' in unitKind and unitKind.split('_')[0]  in SI_order[2]:
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), SI[prefix][2]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), SI[prefix][2], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_DATA' in unitKind and unitKind.split('_')[0]  in DATA_order[0]:
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(DATA.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), DATA[prefix][0]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), DATA[prefix][0], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_DATA' in unitKind and unitKind.split('_')[0]  in DATA_order[1]:
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(DATA.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), DATA[prefix][1]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), DATA[prefix][1], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_OGF' in unitKind and unitKind.split('_')[0] in OGF_order[2]:
            for unitName in list(dictionary[unitKind]):
                # print('O  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for prefix in list(OGF.keys()):
                    # print('S   3: ' + prefix+unitName+'_'+str(SI[prefix]))
                    network.addNode(uNode(prefix+unitName))
                    network.addEdge(conversion(network.getNode(prefix+unitName), network.getNode(unitName), OGF[prefix][2]))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(prefix+unitName), OGF[prefix][2], True))
                    dictionary[unitKind.split('_')[0]].append(prefix+unitName)
        if '_PLURALwS' in unitKind:
            if type(dictionary[unitKind]) is dict:
                listNames = list(dictionary[unitKind].keys())
                for unitName in list(dictionary[unitKind].keys()):
                    # print('U  2: ' + unitName,unitKind.split('_')[0])
                    network.addNode(uNode(unitName))
                    network.addNode(uNode(unitName+'s'))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName+'s'), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName+'s'), network.getNode(unitName), lambda X: X))
                    dictionary[unitKind.split('_')[0]].append(unitName+'s')
                    # for secondName in dictionary[unitKind][unitName] :
                    #     # print('U   3: ' + unitName)
                    #     network.addNode(uNode(secondName))
                    #     network.addNode(uNode(secondName+'s'))
                    #     network.addEdge(conversion(network.getNode(secondName), network.getNode(secondName+'s'), lambda X: X ))
                    #     network.addEdge(conversion(network.getNode(secondName+'s'), network.getNode(secondName), lambda X: X ))
                    #     dictionary[unitKind.split('_')[0]].append(secondName+'s')
            else:
                for unitName in list(dictionary[unitKind]):
                    # print('U  2: ' + unitName,unitKind.split('_')[0])
                    network.addNode(uNode(unitName))
                    network.addNode(uNode(unitName+'s'))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName+'s'), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName+'s'), network.getNode(unitName), lambda X: X))
                    dictionary[unitKind.split('_')[0]].append(unitName+'s')
            if '_UPPER' in unitKind:
                if type( dictionary[unitKind] ) is dict:
                    listNames = list(dictionary[unitKind].keys())
                    for unitName in list(dictionary[unitKind].keys()):
                        # print('U  2: ' + unitName,unitKind.split('_')[0])
                        network.addNode(uNode(unitName))
                        network.addNode(uNode(unitName.upper()+'S'))
                        network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.upper()+'S'), lambda X: X))
                        network.addEdge(conversion(network.getNode(unitName.upper()+'S'), network.getNode(unitName), lambda X: X))
                        dictionary[unitKind.split('_')[0]].append(unitName.upper()+'S')
                        # for secondName in dictionary[unitKind][unitName] :
                        #     # print('U   3: ' + unitName)
                        #     network.addNode(uNode(secondName))
                        #     network.addNode(uNode(secondName.upper()+'S'))
                        #     network.addEdge(conversion(network.getNode(secondName), network.getNode(secondName.upper()+'S'), lambda X: X ))
                        #     network.addEdge(conversion(network.getNode(secondName.upper()+'S'), network.getNode(secondName), lambda X: X ))
                        #     dictionary[unitKind.split('_')[0]].append(secondName.upper()+'S')
                else:
                    for unitName in list( dictionary[unitKind] ):
                        # print('U  2: ' + unitName,unitKind.split('_')[0])
                        network.addNode(uNode(unitName))
                        network.addNode(uNode(unitName.upper()+'S'))
                        network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.upper()+'S'), lambda X: X))
                        network.addEdge(conversion(network.getNode(unitName.upper()+'S'), network.getNode(unitName), lambda X: X))
                        dictionary[unitKind.split('_')[0]].append(unitName.upper()+'S')
        if '_UPPER' in unitKind:
            if type( dictionary[unitKind] ) is dict:
                listNames = list(dictionary[unitKind].keys())
                for unitName in list(dictionary[unitKind].keys()):
                    # print('U  2: ' + unitName,unitKind.split('_')[0])
                    network.addNode(uNode(unitName))
                    network.addNode(uNode(unitName.upper()))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.upper()), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName.upper()), network.getNode(unitName), lambda X: X))
                    dictionary[unitKind.split('_')[0]].append(unitName.upper())
                    for secondName in dictionary[unitKind][unitName]:
                        # print('U   3: ' + unitName)
                        network.addNode(uNode(secondName))
                        network.addNode(uNode(secondName.upper()))
                        network.addEdge(conversion(network.getNode(secondName), network.getNode(secondName.upper()), lambda X: X))
                        network.addEdge(conversion(network.getNode(secondName.upper()), network.getNode(secondName), lambda X: X))
                        dictionary[unitKind.split('_')[0]].append(secondName.upper())
            else:
                for unitName in list( dictionary[unitKind] ):
                    # print('U  2: ' + unitName,unitKind.split('_')[0])
                    network.addNode(uNode(unitName))
                    network.addNode(uNode(unitName.upper()))
                    network.addEdge(conversion(network.getNode(unitName), network.getNode(unitName.upper()), lambda X: X))
                    network.addEdge(conversion(network.getNode(unitName.upper()), network.getNode(unitName), lambda X: X))
                    dictionary[unitKind.split('_')[0]].append(unitName.upper())
        if '_INVERSE' in unitKind:
            pass

    # for unitKind in list(dictionary.keys()) :
    #     if '_REVERSE' in unitKind :
    #         for unitNode in

    # percentage & fraction :
    network.addEdge(conversion(network.getNode('fraction'), network.getNode('percentage'), lambda f: f*100))
    network.addEdge(conversion(network.getNode('percentage'), network.getNode('fraction'), lambda p: p/100))

    # time conversions
    # network.addEdge(conversion(network.getNode('second'), network.getNode('millisecond'), lambda t: t*1000))
    network.addEdge(conversion(network.getNode('minute'), network.getNode('second'), lambda t: t*60))
    network.addEdge(conversion(network.getNode('hour'), network.getNode('minute'), lambda t: t*60))
    network.addEdge(conversion(network.getNode('day'), network.getNode('hour'), lambda t: t*24))
    network.addEdge(conversion(network.getNode('day'), network.getNode('month'), lambda t: t/365.25*12))
    network.addEdge(conversion(network.getNode('week'), network.getNode('day'), lambda t: t*7))
    network.addEdge(conversion(network.getNode('year'), network.getNode('month'), lambda t: t*12))
    network.addEdge(conversion(network.getNode('year'), network.getNode('day'), lambda t: t*36525/100))
    network.addEdge(conversion(network.getNode('lustrum'), network.getNode('year'), lambda t: t*5))
    network.addEdge(conversion(network.getNode('decade'), network.getNode('year'), lambda t: t*10))
    network.addEdge(conversion(network.getNode('century'), network.getNode('year'), lambda t: t*100))

    # temperature conversions
    network.addEdge(conversion(network.getNode('Celsius'), network.getNode('Kelvin'), lambda t: t + 273.15))
    network.addEdge(conversion(network.getNode('Kelvin'), network.getNode('Celsius'), lambda t: t - 273.15))
    network.addEdge(conversion(network.getNode('Celsius'), network.getNode('Fahrenheit'), lambda t: t*9/5 + 32))
    network.addEdge(conversion(network.getNode('Fahrenheit'), network.getNode('Celsius'), lambda t: (t-32) * 5/9))
    network.addEdge(conversion(network.getNode('Fahrenheit'), network.getNode('Rankine'), lambda t: t+459.67))
    network.addEdge(conversion(network.getNode('Rankine'), network.getNode('Fahrenheit'), lambda t: t-459.67))
    network.addEdge(conversion(network.getNode('Rankine'), network.getNode('Kelvin'), lambda t: t*5/9))
    network.addEdge(conversion(network.getNode('Kelvin'), network.getNode('Rankine'), lambda t: t*9/5))

    # length conversions
    network.addEdge(conversion(network.getNode('yard'), network.getNode('meter'), lambda d: d*9144/10000))
    # network.addEdge(conversion(network.getNode('foot'), network.getNode('meter'), lambda d: d*0.3048))
    network.addEdge(conversion(network.getNode('inch'), network.getNode('thou'), lambda d: d*1000))
    network.addEdge(conversion(network.getNode('foot'), network.getNode('inch'), lambda d: d*12))
    network.addEdge(conversion(network.getNode('yard'), network.getNode('foot'), lambda d: d*3))
    network.addEdge(conversion(network.getNode('chain'), network.getNode('yard'), lambda d: d*22))
    network.addEdge(conversion(network.getNode('furlong'), network.getNode('chain'), lambda d: d*10))
    network.addEdge(conversion(network.getNode('mile'), network.getNode('furlong'), lambda d: d*8))
    network.addEdge(conversion(network.getNode('league'), network.getNode('mile'), lambda d: d*3))
    network.addEdge(conversion(network.getNode('nautical league'), network.getNode('nautical mile'), lambda d: d*3))
    network.addEdge(conversion(network.getNode('nautical mile'), network.getNode('meter'), lambda d: d*1852))
    network.addEdge(conversion(network.getNode('rod'), network.getNode('yard'), lambda d: d*55/10))

    # area conversions
    network.addEdge(conversion(network.getNode('square mile'), network.getNode('acre'), lambda d: d*640))
    network.addEdge(conversion(network.getNode('acre'), network.getNode('square yard'), lambda d: d*4840))
    network.addEdge(conversion(network.getNode('square rod'), network.getNode('square yard'), lambda d: d*3025/100))
    network.addEdge(conversion(network.getNode('square yard'), network.getNode('square foot'), lambda d: d*9))
    network.addEdge(conversion(network.getNode('square foot'), network.getNode('square inch'), lambda d: d*144))
    network.addEdge(conversion(network.getNode('square foot'), network.getNode('square meter'), lambda d: d*(3048**2)/(10000**2)))
    network.addEdge(conversion(network.getNode('Darcy'), network.getNode('mD'), lambda d: d*1000))
    network.addEdge(conversion(network.getNode('Darcy'), network.getNode('µm2'), lambda d: d*0.9869233))
    # network.addEdge(conversion(network.getNode('m*m'), network.getNode('m'), lambda d: d**0.5))
    # network.addEdge(conversion(network.getNode('m'), network.getNode('m*m'), lambda d: d**2))
    # network.addEdge(conversion(network.getNode('rd*rd'), network.getNode('rd'), lambda d: d**0.5))
    # network.addEdge(conversion(network.getNode('rd'), network.getNode('rd*rd'), lambda d: d**2))
    # network.addEdge(conversion(network.getNode('yd*yd'), network.getNode('yd'), lambda d: d**0.5))
    # network.addEdge(conversion(network.getNode('yd'), network.getNode('yd*yd'), lambda d: d**2))
    # network.addEdge(conversion(network.getNode('ft*ft'), network.getNode('ft'), lambda d: d**0.5))
    # network.addEdge(conversion(network.getNode('ft'), network.getNode('ft*ft'), lambda d: d**2))
    # network.addEdge(conversion(network.getNode('in*in'), network.getNode('in'), lambda d: d**0.5))
    # network.addEdge(conversion(network.getNode('in'), network.getNode('in*in'), lambda d: d**2))

    # volume conversions
    network.addEdge(conversion(network.getNode('gill'), network.getNode('fuild ounce'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('pint'), network.getNode('gill'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('quart'), network.getNode('pint'), lambda v: v*2))
    network.addEdge(conversion(network.getNode('gallonUS'), network.getNode('fuild ounce'), lambda v: v*128))
    network.addEdge(conversion(network.getNode('gallonUS'), network.getNode('quart'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('gallonUS'), network.getNode('cubic inch'), lambda v: v*231))
    
    network.addEdge(conversion(network.getNode('gallonUK'), network.getNode('quartUK'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('gallonUK'), network.getNode('fuild ounce UK'), lambda v: v*160))
    network.addEdge(conversion(network.getNode('gallonUK'), network.getNode('litre'), lambda v: v*4.54609))
    network.addEdge(conversion(network.getNode('gillUK'), network.getNode('fuild ounce UK'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('pintUK'), network.getNode('gillUK'), lambda v: v*4))
    network.addEdge(conversion(network.getNode('quartUK'), network.getNode('pintUK'), lambda v: v*2))
    
    network.addEdge(conversion(network.getNode('gallonUK'), network.getNode('liter'), lambda v: v* 4.54609))
    network.addEdge(conversion(network.getNode('cubic foot'), network.getNode('cubic meter'), lambda v: v*(3048**3)/(10000**3)))
    network.addEdge(conversion(network.getNode('standard cubic foot'), network.getNode('standard cubic meter'), lambda v: v*(3048**3)/(10000**3)))
    network.addEdge(conversion(network.getNode('standard barrel'), network.getNode('USgal'), lambda v: v*42))
    network.addEdge(conversion(network.getNode('standard cubic meter'), network.getNode('standard barrel'), lambda v: v*6.289814))
    network.addEdge(conversion(network.getNode('standard barrel'), network.getNode('standard cubic foot'), lambda v: v*5.614584))
    network.addEdge(conversion(network.getNode('reservoir cubic meter'), network.getNode('reservoir barrel'), lambda v: v*6.289814))
    network.addEdge(conversion(network.getNode('reservoir cubic meter'), network.getNode('standard cubic meter'), lambda v: v / network.get_fvf()))
    # network.addEdge(conversion(network.getNode('standard cubic meter'), network.getNode('standard cubic foot'), lambda v: v/5.614584))

    # pressure conversions
    network.addEdge(conversion(network.getNode('psi gauge'), network.getNode('absolute psi'), lambda p: p+14.6959))
    network.addEdge(conversion(network.getNode('absolute psi'), network.getNode('psi gauge'), lambda p: p-14.6959))
    network.addEdge(conversion(network.getNode('bar gauge'), network.getNode('absolute bar'), lambda p: p+1.01325))
    network.addEdge(conversion(network.getNode('absolute bar'), network.getNode('bar gauge'), lambda p: p-1.01325))

    network.addEdge(conversion(network.getNode('absolute bar'), network.getNode('absolute psi'), lambda p: p*14.50377377322))
    network.addEdge(conversion(network.getNode('bar gauge'), network.getNode('psi gauge'), lambda p: p*14.50377377322))
    network.addEdge(conversion(network.getNode('absolute bar'), network.getNode('Pascal'), lambda p: p*100000))
    # network.addEdge(conversion(network.getNode('atmosphere'), network.getNode('absolute bar'), lambda p: p*1.01325))
    network.addEdge(conversion(network.getNode('atmosphere'), network.getNode('Pascal'), lambda p: p*101325))
    network.addEdge(conversion(network.getNode('atmosphere'), network.getNode('Torr'), lambda p: p*760))

    # mass conversion
    network.addEdge(conversion(network.getNode('grain'), network.getNode('milligrams'), lambda w: w*64.7989))
    network.addEdge(conversion(network.getNode('pennyweight'), network.getNode('grain'), lambda w: w*24))
    network.addEdge(conversion(network.getNode('dram'), network.getNode('pound'), lambda w: w/256))
    network.addEdge(conversion(network.getNode('stone'), network.getNode('pound'), lambda w: w*14))
    network.addEdge(conversion(network.getNode('quarter'), network.getNode('stone'), lambda w: w*2))
    network.addEdge(conversion(network.getNode('ounce'), network.getNode('dram'), lambda w: w*16))
    network.addEdge(conversion(network.getNode('pound'), network.getNode('ounce'), lambda w: w*16))
    network.addEdge(conversion(network.getNode('long hundredweight'), network.getNode('quarter'), lambda w: w*4))
    network.addEdge(conversion(network.getNode('short hundredweight'), network.getNode('pound'), lambda w: w*100))
    network.addEdge(conversion(network.getNode('short ton'), network.getNode('short hundredweight'), lambda w: w*20))
    network.addEdge(conversion(network.getNode('long ton'), network.getNode('long hundredweight'), lambda w: w*20))

    network.addEdge(conversion(network.getNode('metric ton'), network.getNode('kilogram'), lambda w: w*1000))
    network.addEdge(conversion(network.getNode('kilogram'), network.getNode('gram'), lambda w: w*1000))
    # network.addEdge(conversion(network.getNode('pound'), network.getNode('gram'), lambda w: w*453.59237))
    network.addEdge(conversion(network.getNode('pound'), network.getNode('kilogram'), lambda w: w*45359237/100000000))

    # force conversion
    # network.addEdge(conversion(network.getNode('kilogram'), network.getNode('kilogram force'), lambda f: f* converter(StandadEarthGravity,'m/s2','cm/s2',False)))
    network.addEdge(conversion(network.getNode('kilogram mass'), network.getNode('kilogram force'), lambda f: f * StandadEarthGravity))
    network.addEdge(conversion(network.getNode('kilogram force'), network.getNode('kilogram mass'), lambda f: f / StandadEarthGravity))
    network.addEdge(conversion(network.getNode('Dyne'), network.getNode('Newton'), lambda f: f*1E-5))
    network.addEdge(conversion(network.getNode('Newton'), network.getNode('Dyne'), lambda f: f*1E5 ))

    # energy conversion
    network.addEdge(conversion(network.getNode('Joule'), network.getNode('gram calorie'), lambda e: e/4.184))
    network.addEdge(conversion(network.getNode('Kilojoule'), network.getNode('Joule'), lambda e: e*1000))
    network.addEdge(conversion(network.getNode('Kilojoule'), network.getNode('kilowatt hour'), lambda e: e/3600))
    network.addEdge(conversion(network.getNode('Kilojoule'), network.getNode('British thermal unit'), lambda e: e/1.055))

    # power conversion
    network.addEdge(conversion(network.getNode('Horsepower'), network.getNode('Watt'), lambda e: e*745.699872))

    # density conversion
    network.addEdge(conversion(network.getNode('API'), network.getNode('SgO'), lambda d: 141.5/(131.5+d)))
    network.addEdge(conversion(network.getNode('SgO'), network.getNode('API'), lambda d: 141.5/d-131.5))
    network.addEdge(conversion(network.getNode('SgO'), network.getNode('g/cc'), lambda d: d))
    network.addEdge(conversion(network.getNode('SgW'), network.getNode('g/cc'), lambda d: d))
    network.addEdge(conversion(network.getNode('SgG'), network.getNode('g/cc'), lambda d: d * StandardAirDensity))
    network.addEdge(conversion(network.getNode('psia/ft'), network.getNode('lb/ft3'), lambda d: d*144))
    network.addEdge(conversion(network.getNode('g/cm3'), network.getNode('lb/ft3'), lambda d: d*62.427960576144606))
    network.addEdge(conversion(network.getNode('lb/ft3'), network.getNode('lb/stb'), lambda d: d*5.614584))

    # viscosity conversions
    network.addEdge(conversion(network.getNode('Pa*s'), network.getNode('Poise'), lambda v: v*10))

    # data conversions
    network.addEdge(conversion(network.getNode('byte'), network.getNode('bit'), lambda d: d*8))
    network.addEdge(conversion(network.getNode('byte'), network.getNode('B'), lambda d: d))
    network.addEdge(conversion(network.getNode('bit'), network.getNode('b'), lambda d: d))

    for unitKind in list(dictionary.keys()):
        if '_REVERSE' in unitKind:
            if type(dictionary[unitKind]) is dict:
                nameList = list(dictionary[unitKind].keys())
            else:
                nameList = list(dictionary[unitKind])
            # print(nameList)
            for unitName in nameList:
                # print('R  2: ' + unitName)
                for otherName in network.childrenOf( network.getNode(unitName)):
                    # print('R   3: '+unitName,otherName.getName())
                    if network.getNode(unitName)!=otherName:
                        network.addEdge(conversion(otherName, network.getNode(unitName), network.edges[network.getNode(unitName)][1][network.edges[network.getNode(unitName)][0].index(otherName) ], True))

    for unitKind in list(dictionary.keys()):
        if '_FROMvolume' in unitKind and unitKind.split('_')[0] in SI_order[2]:
            # if '_SI' in unitKind and unitKind.split('_')[0]  in SI_order[2] :
            for unitName in list(dictionary[unitKind]):
                # print('S  2: ' + unitName)
                network.addNode(uNode(unitName))
                dictionary[unitKind.split('_')[0]].append(unitName)
                for otherName in network.childrenOf( network.getNode(unitName.split('/')[0])):
                    if network.getNode(unitName.split('/')[0])!=otherName:
                        print('R   3: '+unitName,otherName.getName())
                        otherRate = otherName.getName() +'/'+ unitName.split('/')[1]
                        network.addNode(uNode(otherRate))
                        network.addEdge(conversion(network.getNode(unitName), otherRate, network.edges[ network.getNode(unitName.split('/')[1]) ][1][network.edges[network.getNode(unitName.split('/')[1])][0].index(otherName)]))
                        network.addEdge(conversion(otherRate, network.getNode(unitName), network.edges[ network.getNode(unitName.split('/')[1]) ][1][network.edges[network.getNode(unitName.split('/')[1]) ][0].index(otherName) ], True))


    toRemove = []
    for unitKind in dictionary:
        if '_' in unitKind:
            toRemove.append(unitKind)
        else : # if '_' not in unitKind :
            dictionary[unitKind] = tuple(dictionary[unitKind])
    dictionary['userUnits'] = []

    for unitKind in toRemove:
        dictionary.pop(unitKind)

    return network


def _create_rates():
    # volumes / time
    rates = list(dictionary['rate']) if 'rate' in dictionary else []
    # for volume in dictionary['volume']:
    #     for time in dictionary['time']:
    #         rates.append(volume+'/'+time)
    rates += [volume+'/'+time for volume in dictionary['volume'] for time in dictionary['time']]
    # for weight in dictionary['weight']:
    #     for time in dictionary['time']:
    #         rates.append(weight+'/'+time)
    rates += [weight+'/'+time for weight in dictionary['weight'] for time in dictionary['time']]
    # data / time
    # for data in dictionary['dataBYTE']:
    #     for time in dictionary['time']:
    #         rates.append(data+'/'+time)
    rates += [data+'/'+time for data in dictionary['dataBYTE'] for time in dictionary['time']]
    # for data in dictionary['dataBIT']:
    #     for time in dictionary['time']:
    #         rates.append(data+'/'+time)
    rates += [data+'/'+time for data in dictionary['dataBIT'] for time in dictionary['time']]
    dictionary['rate'] = tuple(set(rates))


def _create_volumeRatio():
    # volume / volume
    ratio = list(dictionary['volumeRatio']) if 'volumeRatio' in dictionary else []
    # for numerator in dictionary['volume']:
    #     for denominator in dictionary['volume']:
    #         ratio.append(numerator+'/'+denominator)
    ratio += [numerator+'/'+denominator for numerator in dictionary['volume'] for denominator in dictionary['volume']]
    dictionary['volumeRatio'] = tuple(set(ratio))


def _create_density():
    # mass / volume
    density = list(dictionary['density']) if 'density' in dictionary else []
    # for mass in dictionary['mass']:
    #     for volume in dictionary['volume']:
    #         density.append(mass+'/'+volume)
    density += [mass+'/'+volume for mass in dictionary['mass'] for volume in dictionary['volume']]
    dictionary['density'] = tuple(set(density))


def _create_speed():
    # length / time
    speed = list(dictionary['speed']) if 'speed' in dictionary else []
    # for length in dictionary['length']:
    #     for time in dictionary['time']:
    #         speed.append(length+'/'+time)
    speed += [length+'/'+time for length in dictionary['length'] for time in dictionary['time']]
    dictionary['speed'] = tuple(set(speed))
    
    
def _create_power():
    # length / time
    power = list(dictionary['power']) if 'power' in dictionary else []
    # for energy in dictionary['energy']:
    #     for time in dictionary['time']:
    #         power.append(energy+'/'+time)
    power += [energy+'/'+time for energy in dictionary['energy'] for time in dictionary['time']]
    dictionary['power'] = tuple(set(power))


def _create_productivityIndex():
    # volume / time / pressure
    productivityIndex = list(dictionary['productivityIndex']) if 'productivityIndex' in dictionary else []
    # for volume in dictionary['volume']:
    #     for time in dictionary['time']:
    #         for pressure in dictionary['pressure']:
    #             productivityIndex.append(volume+'/'+time+'/'+pressure)
    productivityIndex += [volume+'/'+time+'/'+pressure 
                          for volume in dictionary['volume'] 
                          for time in dictionary['time'] 
                          for pressure in dictionary['pressure']]
    dictionary['productivityIndex'] = tuple(set(productivityIndex))


def _create_pressureGradient():
    # pressure / length
    pressureGradient = list(dictionary['pressureGradient']) if 'pressureGradient' in dictionary else []
    # for pressure in dictionary['pressure']:
    #     for length in dictionary['length']:
    #         pressureGradient.append(pressure+'/'+length)
    pressureGradient += [pressure+'/'+length for pressure in dictionary['pressure'] for length in dictionary['length']]
    dictionary['pressureGradient'] = tuple(set(pressureGradient))
    

def _create_temperatureGradient():
    # pressure / length
    temperatureGradient = list(dictionary['temperatureGradient']) if 'temperatureGradient' in dictionary else []
    # for pressure in dictionary['pressure']:
    #     for length in dictionary['length']:
    #         pressureGradient.append(pressure+'/'+length)
    temperatureGradient += [temperature+'/'+length for temperature in dictionary['temperature'] for length in dictionary['length']]
    dictionary['temperatureGradient'] = tuple(set(temperatureGradient))
    

def _create_acceleration():
    # length / time / time
    acceleration = list(dictionary['acceleration']) if 'acceleration' in dictionary else []
    # for length in dictionary['length']:
    #     for time1 in dictionary['time']:
    #         for time2 in dictionary['time']:
    #             if time1 == time2:
    #                 acceleration.append(length+'/'+time1+'2')
    #             else:
    #                 acceleration.append(length+'/'+time1+'/'+time2)
    acceleration += [(length+'/'+time1+'2') if time1 == time2 else (length+'/'+time1+'/'+time2)
                     for length in dictionary['length']
                     for time1 in dictionary['time']
                     for time2 in dictionary['time']]
    dictionary['acceleration'] = tuple(set(acceleration))


# load the network into an instance of the grath database
unitsNetwork = _loadNetwork()

# load the diccionary with ratio unis
_create_rates()
_create_volumeRatio()
_create_density()
_create_speed()
_create_productivityIndex()
_create_pressureGradient()
_create_temperatureGradient()
_create_power()


def network2Frame():
    network=unitsNetwork
    from pandas import DataFrame
    Frame = DataFrame(data={},columns=['source','target','lambda'])

    i = 0
    for node in network.edges:
        for children in network.childrenOf(node):
            Frame.loc[i,['source', 'target', 'lambda']] = [node.getName(), children.getName(), network.conversion(node, children)]
            i += 1
            #Frame.loc[i,'source'] = node.getName()
            #Frame.loc[i,'target'] = children.getName()
            #Frame.loc[i,'lambda'] = network.conversion(node,children)

    return Frame.drop_duplicates(['source', 'target'])