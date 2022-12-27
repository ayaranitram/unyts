#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:36:48 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['unitsNetwork']

from .dictionaries import SI, SI_order, OGF, OGF_order, DATA, DATA_order, dictionary, StandardAirDensity, \
    StandardEarthGravity
from .parameters import unyts_parameters_, dir_path
from cloudpickle import dump, load
from os.path import isfile
from json import dump as jdump
from tempfile import gettempdir


class UNode(object):
    def __init__(self, name):
        self.name = name if type(name) is str else ''

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name


class UDigraph(object):
    """edges is a dict mapping each node to a list of its children"""

    def __init__(self) -> None:
        self.edges = {}
        self.previous = [(None, None)]
        self.recursion_limit = 5
        self.fvf = None
        self.memory = {}
        self.fvf = None
        self.print = False

    def add_node(self, node) -> None:
        if node in self.edges:
            raise ValueError('Duplicate node')
        else:
            self.edges[node] = [], []

    def add_edge(self, edge, reverse=False) -> None:
        src = edge.get_source()
        dest = edge.get_destination()
        conv = edge.get_convert()
        if not (src in self.edges and dest in self.edges):
            raise ValueError('Node not in graph')
        self.edges[src][0].append(dest)
        self.edges[src][1].append(conv)

    def children_of(self, node):
        return self.edges[node][0]

    def has_node(self, node):
        if type(node) is str:
            return node in [n.get_name() for n in self.edges]
        else:
            return node in self.edges

    def get_node(self, name):
        for n in self.edges:
            if n.get_name() == name:
                return n
        raise NameError(name)

    def list_nodes(self):
        return list(set([N.get_name() for N in self.edge.keys()]))

    def convert(self, value, src, dest):
        if type(src) != UNode:
            src = self.get_node(src)
        if type(dest) != UNode:
            dest = self.get_node(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)](value)

    def conversion(self, src, dest):
        if type(src) != UNode:
            src = self.get_node(src)
        if type(dest) != UNode:
            dest = self.get_node(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)]

    def __str__(self):
        result = ''
        for src in self.edges:
            for dest in self.edges[src]:
                result = result + src.get_name() + '->' \
                         + dest.get_name() + \
                         str(self.conv) + '\n'
        return result[:-1]  # remove final newline

    def set_fvf(self, FVF) -> None:
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


class Conversion(object):
    def __init__(self, src, dest, conv, reverse=False):
        """Assumes src and dest are nodes"""
        self.src = src
        self.dest = dest
        self.conv = conv
        self.rev = reverse

    def get_source(self):
        return self.src

    def get_destination(self):
        return self.dest

    def convert(self, value):
        return self.conv(value)

    def reverse(self, value):
        return value / self.conv(1)

    def get_convert(self):
        if self.rev and self.conv is not None:
            return lambda X: X / self.conv(1)
        else:
            return self.conv

    def __str__(self):
        return self.src.get_name() + '->' + self.dest.get_name()


def _load_network():
    print('preparing units network...')
    network = UDigraph()

    for unit_kind in list(dictionary.keys()):
        # print('1: ' +unit_kind)
        if '_' not in unit_kind:
            for unit_name in dictionary[unit_kind]:
                # print('_ 2: ' + unit_name)
                network.add_node(UNode(unit_name))
        if '_NAMES' in unit_kind:
            for unit_name in list(dictionary[unit_kind].keys()):
                # print('N  2: ' + unit_name,unit_kind.split('_')[0])
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for secondName in dictionary[unit_kind][unit_name]:
                    # print('N   3: ' + unit_name)
                    network.add_node(UNode(secondName))
                    network.add_edge(Conversion(network.get_node(secondName), network.get_node(unit_name), lambda X: X))
                    network.add_edge(Conversion(network.get_node(unit_name), network.get_node(secondName), lambda X: X))
                    dictionary[unit_kind.split('_')[0]].append(secondName)
                # for secondName in dictionary[unit_kind][unit_name]:
                #     for t in range(dictionary[unit_kind][unit_name].index(secondName)+1, len(dictionary[unit_kind][unit_name])):
                #         thirdName = dictionary[unit_kind][unit_name][t]
                #         network.addEdge(Conversion(network.getNode(secondName), network.getNode(thirdName), lambda X: X))
                #         network.addEdge(Conversion(network.getNode(thirdName), network.getNode(secondName), lambda X: X))

        if '_SPACES' in unit_kind:
            for unit_name in list(dictionary[unit_kind].keys()):
                # print('N  2: ' + unit_name,unit_kind.split('_')[0])
                if ' ' in unit_name:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.replace(' ', '-')))
                    dictionary[unit_kind.split('_')[0]].append(unit_name)
                    dictionary[unit_kind.split('_')[0]].append(unit_name.replace(' ', '-'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.replace(' ', '-')),
                                   lambda X: X))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.replace(' ', '-')),
                                   lambda X: X))
                    for secondName in dictionary[unit_kind][unit_name]:
                        # print('N   3: ' + unit_name)
                        if ' ' in secondName:
                            network.add_node(UNode(secondName))
                            network.add_node(UNode(secondName.replace(' ', '-')))
                            network.add_edge(
                                Conversion(network.get_node(secondName.replace(' ', '-')), network.get_node(secondName),
                                           lambda X: X))
                            network.add_edge(
                                Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', '-')),
                                           lambda X: X))
                            dictionary[unit_kind.split('_')[0]].append(secondName)
                            dictionary[unit_kind.split('_')[0]].append(secondName.replace(' ', '-'))
                else:
                    for secondName in dictionary[unit_kind][unit_name]:
                        # print('N   3: ' + unit_name)
                        if ' ' in secondName:
                            network.add_node(UNode(secondName))
                            network.add_node(UNode(secondName.replace(' ', '-')))
                            network.add_edge(
                                Conversion(network.get_node(secondName.replace(' ', '-')), network.get_node(secondName),
                                           lambda X: X))
                            network.add_edge(
                                Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', '-')),
                                           lambda X: X))
                            dictionary[unit_kind.split('_')[0]].append(secondName)
                            dictionary[unit_kind.split('_')[0]].append(secondName.replace(' ', '-'))

        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[0]:
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix][0]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][0],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[1]:
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix][1]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][1],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(SI.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][2],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_DATA' in unit_kind and unit_kind.split('_')[0] in DATA_order[0]:
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(DATA.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), DATA[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), DATA[prefix][0],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_DATA' in unit_kind and unit_kind.split('_')[0] in DATA_order[1]:
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(DATA.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), DATA[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), DATA[prefix][1],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_OGF' in unit_kind and unit_kind.split('_')[0] in OGF_order[2]:
            for unit_name in list(dictionary[unit_kind]):
                # print('O  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in list(OGF.keys()):
                    # print('S   3: ' + prefix+unit_name+'_'+str(SI[prefix]))
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), OGF[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), OGF[prefix][2],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_PLURALwS' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                list_names = list(dictionary[unit_kind].keys())
                for unit_name in list(dictionary[unit_kind].keys()):
                    # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), lambda X: X))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), lambda X: X))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
                    # for secondName in dictionary[unit_kind][unit_name] :
                    #     # print('U   3: ' + unit_name)
                    #     network.addNode(uNode(secondName))
                    #     network.addNode(uNode(secondName+'s'))
                    #     network.addEdge(Conversion(network.getNode(secondName), network.getNode(secondName+'s'), lambda X: X ))
                    #     network.addEdge(Conversion(network.getNode(secondName+'s'), network.getNode(secondName), lambda X: X ))
                    #     dictionary[unit_kind.split('_')[0]].append(secondName+'s')
            else:
                for unit_name in list(dictionary[unit_kind]):
                    # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), lambda X: X))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), lambda X: X))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
            if '_UPPER' in unit_kind:
                if type(dictionary[unit_kind]) is dict:
                    list_names = list(dictionary[unit_kind].keys())
                    for unit_name in list(dictionary[unit_kind].keys()):
                        # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       lambda X: X))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       lambda X: X))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
                        # for secondName in dictionary[unit_kind][unit_name] :
                        #     # print('U   3: ' + unit_name)
                        #     network.addNode(uNode(secondName))
                        #     network.addNode(uNode(secondName.upper()+'S'))
                        #     network.addEdge(Conversion(network.getNode(secondName), network.getNode(secondName.upper()+'S'), lambda X: X ))
                        #     network.addEdge(Conversion(network.getNode(secondName.upper()+'S'), network.getNode(secondName), lambda X: X ))
                        #     dictionary[unit_kind.split('_')[0]].append(secondName.upper()+'S')
                else:
                    for unit_name in list(dictionary[unit_kind]):
                        # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       lambda X: X))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       lambda X: X))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
        if '_UPPER' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                list_names = list(dictionary[unit_kind].keys())
                for unit_name in list(dictionary[unit_kind].keys()):
                    # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), lambda X: X))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), lambda X: X))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
                    for secondName in dictionary[unit_kind][unit_name]:
                        # print('U   3: ' + unit_name)
                        network.add_node(UNode(secondName))
                        network.add_node(UNode(secondName.upper()))
                        network.add_edge(
                            Conversion(network.get_node(secondName), network.get_node(secondName.upper()), lambda X: X))
                        network.add_edge(
                            Conversion(network.get_node(secondName.upper()), network.get_node(secondName), lambda X: X))
                        dictionary[unit_kind.split('_')[0]].append(secondName.upper())
            else:
                for unit_name in list(dictionary[unit_kind]):
                    # print('U  2: ' + unit_name,unit_kind.split('_')[0])
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), lambda X: X))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), lambda X: X))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
        if '_INVERSE' in unit_kind:
            pass

    # for unit_kind in list(dictionary.keys()) :
    #     if '_REVERSE' in unit_kind :
    #         for unitNode in

    # percentage & fraction :
    network.add_edge(Conversion(network.get_node('fraction'), network.get_node('percentage'), lambda f: f * 100))
    network.add_edge(Conversion(network.get_node('percentage'), network.get_node('fraction'), lambda p: p / 100))

    # time conversions
    # network.addEdge(Conversion(network.getNode('second'), network.getNode('millisecond'), lambda t: t*1000))
    network.add_edge(Conversion(network.get_node('minute'), network.get_node('second'), lambda t: t * 60))
    network.add_edge(Conversion(network.get_node('hour'), network.get_node('minute'), lambda t: t * 60))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('hour'), lambda t: t * 24))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('month'), lambda t: t / 365.25 * 12))
    network.add_edge(Conversion(network.get_node('week'), network.get_node('day'), lambda t: t * 7))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('month'), lambda t: t * 12))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('day'), lambda t: t * 36525 / 100))
    network.add_edge(Conversion(network.get_node('lustrum'), network.get_node('year'), lambda t: t * 5))
    network.add_edge(Conversion(network.get_node('decade'), network.get_node('year'), lambda t: t * 10))
    network.add_edge(Conversion(network.get_node('century'), network.get_node('year'), lambda t: t * 100))

    # temperature conversions
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Kelvin'), lambda t: t + 273.15))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Celsius'), lambda t: t - 273.15))
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Fahrenheit'), lambda t: t * 9 / 5 + 32))
    network.add_edge(
        Conversion(network.get_node('Fahrenheit'), network.get_node('Celsius'), lambda t: (t - 32) * 5 / 9))
    network.add_edge(Conversion(network.get_node('Fahrenheit'), network.get_node('Rankine'), lambda t: t + 459.67))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Fahrenheit'), lambda t: t - 459.67))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Kelvin'), lambda t: t * 5 / 9))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Rankine'), lambda t: t * 9 / 5))

    # length conversions
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('meter'), lambda d: d * 9144 / 10000))
    # network.addEdge(Conversion(network.getNode('foot'), network.getNode('meter'), lambda d: d*0.3048))
    network.add_edge(Conversion(network.get_node('inch'), network.get_node('thou'), lambda d: d * 1000))
    network.add_edge(Conversion(network.get_node('foot'), network.get_node('inch'), lambda d: d * 12))
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('foot'), lambda d: d * 3))
    network.add_edge(Conversion(network.get_node('chain'), network.get_node('yard'), lambda d: d * 22))
    network.add_edge(Conversion(network.get_node('furlong'), network.get_node('chain'), lambda d: d * 10))
    network.add_edge(Conversion(network.get_node('mile'), network.get_node('furlong'), lambda d: d * 8))
    network.add_edge(Conversion(network.get_node('league'), network.get_node('mile'), lambda d: d * 3))
    network.add_edge(
        Conversion(network.get_node('nautical league'), network.get_node('nautical mile'), lambda d: d * 3))
    network.add_edge(Conversion(network.get_node('nautical mile'), network.get_node('meter'), lambda d: d * 1852))
    network.add_edge(Conversion(network.get_node('rod'), network.get_node('yard'), lambda d: d * 55 / 10))

    # area conversions
    network.add_edge(Conversion(network.get_node('square mile'), network.get_node('acre'), lambda d: d * 640))
    network.add_edge(Conversion(network.get_node('acre'), network.get_node('square yard'), lambda d: d * 4840))
    network.add_edge(
        Conversion(network.get_node('square rod'), network.get_node('square yard'), lambda d: d * 3025 / 100))
    network.add_edge(Conversion(network.get_node('square yard'), network.get_node('square foot'), lambda d: d * 9))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square inch'), lambda d: d * 144))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square meter'),
                                lambda d: d * (3048 ** 2) / (10000 ** 2)))
    network.add_edge(Conversion(network.get_node('Darcy'), network.get_node('mD'), lambda d: d * 1000))
    network.add_edge(Conversion(network.get_node('Darcy'), network.get_node('µm2'), lambda d: d * 0.9869233))
    # network.addEdge(Conversion(network.getNode('m*m'), network.getNode('m'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('m'), network.getNode('m*m'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('rd*rd'), network.getNode('rd'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('rd'), network.getNode('rd*rd'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('yd*yd'), network.getNode('yd'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('yd'), network.getNode('yd*yd'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('ft*ft'), network.getNode('ft'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('ft'), network.getNode('ft*ft'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('in*in'), network.getNode('in'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('in'), network.getNode('in*in'), lambda d: d**2))

    # volume conversions
    network.add_edge(Conversion(network.get_node('gill'), network.get_node('fuild ounce'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('pint'), network.get_node('gill'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('quart'), network.get_node('pint'), lambda v: v * 2))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('fuild ounce'), lambda v: v * 128))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('quart'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('cubic inch'), lambda v: v * 231))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('quartUK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('fuild ounce UK'), lambda v: v * 160))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('litre'), lambda v: v * 4.54609))
    network.add_edge(Conversion(network.get_node('gillUK'), network.get_node('fuild ounce UK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('pintUK'), network.get_node('gillUK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('quartUK'), network.get_node('pintUK'), lambda v: v * 2))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('liter'), lambda v: v * 4.54609))
    network.add_edge(Conversion(network.get_node('cubic foot'), network.get_node('cubic meter'),
                                lambda v: v * (3048 ** 3) / (10000 ** 3)))
    network.add_edge(Conversion(network.get_node('standard cubic foot'), network.get_node('standard cubic meter'),
                                lambda v: v * (3048 ** 3) / (10000 ** 3)))
    network.add_edge(Conversion(network.get_node('standard barrel'), network.get_node('USgal'), lambda v: v * 42))
    network.add_edge(
        Conversion(network.get_node('standard cubic meter'), network.get_node('standard barrel'),
                   lambda v: v * 6.289814))
    network.add_edge(
        Conversion(network.get_node('standard barrel'), network.get_node('standard cubic foot'),
                   lambda v: v * 5.614584))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('reservoir barrel'),
                                lambda v: v * 6.289814))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('standard cubic meter'),
                                lambda v: v / network.get_fvf()))
    # network.addEdge(Conversion(network.getNode('standard cubic meter'), network.getNode('standard cubic foot'), lambda v: v/5.614584))

    # pressure conversions
    network.add_edge(Conversion(network.get_node('psi gauge'), network.get_node('absolute psi'), lambda p: p + 14.6959))
    network.add_edge(Conversion(network.get_node('absolute psi'), network.get_node('psi gauge'), lambda p: p - 14.6959))
    network.add_edge(Conversion(network.get_node('bar gauge'), network.get_node('absolute bar'), lambda p: p + 1.01325))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('bar gauge'), lambda p: p - 1.01325))

    network.add_edge(
        Conversion(network.get_node('absolute bar'), network.get_node('absolute psi'), lambda p: p * 14.50377377322))
    network.add_edge(
        Conversion(network.get_node('bar gauge'), network.get_node('psi gauge'), lambda p: p * 14.50377377322))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('Pascal'), lambda p: p * 100000))
    # network.addEdge(Conversion(network.getNode('atmosphere'), network.getNode('absolute bar'), lambda p: p*1.01325))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Pascal'), lambda p: p * 101325))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Torr'), lambda p: p * 760))

    # mass Conversion
    network.add_edge(Conversion(network.get_node('grain'), network.get_node('milligrams'), lambda w: w * 64.7989))
    network.add_edge(Conversion(network.get_node('pennyweight'), network.get_node('grain'), lambda w: w * 24))
    network.add_edge(Conversion(network.get_node('dram'), network.get_node('pound'), lambda w: w / 256))
    network.add_edge(Conversion(network.get_node('stone'), network.get_node('pound'), lambda w: w * 14))
    network.add_edge(Conversion(network.get_node('quarter'), network.get_node('stone'), lambda w: w * 2))
    network.add_edge(Conversion(network.get_node('ounce'), network.get_node('dram'), lambda w: w * 16))
    network.add_edge(Conversion(network.get_node('pound'), network.get_node('ounce'), lambda w: w * 16))
    network.add_edge(Conversion(network.get_node('long hundredweight'), network.get_node('quarter'), lambda w: w * 4))
    network.add_edge(Conversion(network.get_node('short hundredweight'), network.get_node('pound'), lambda w: w * 100))
    network.add_edge(
        Conversion(network.get_node('short ton'), network.get_node('short hundredweight'), lambda w: w * 20))
    network.add_edge(Conversion(network.get_node('long ton'), network.get_node('long hundredweight'), lambda w: w * 20))

    network.add_edge(Conversion(network.get_node('metric ton'), network.get_node('kilogram'), lambda w: w * 1000))
    network.add_edge(Conversion(network.get_node('kilogram'), network.get_node('gram'), lambda w: w * 1000))
    # network.addEdge(Conversion(network.getNode('pound'), network.getNode('gram'), lambda w: w*453.59237))
    network.add_edge(
        Conversion(network.get_node('pound'), network.get_node('kilogram'), lambda w: w * 45359237 / 100000000))

    # force Conversion
    # network.addEdge(Conversion(network.getNode('kilogram'), network.getNode('kilogram force'), lambda f: f* converter(StandardEarthGravity,'m/s2','cm/s2',False)))
    network.add_edge(Conversion(network.get_node('kilogram mass'), network.get_node('kilogram force'),
                                lambda f: f * StandardEarthGravity))
    network.add_edge(Conversion(network.get_node('kilogram force'), network.get_node('kilogram mass'),
                                lambda f: f / StandardEarthGravity))
    network.add_edge(Conversion(network.get_node('Dyne'), network.get_node('Newton'), lambda f: f * 1E-5))
    network.add_edge(Conversion(network.get_node('Newton'), network.get_node('Dyne'), lambda f: f * 1E5))

    # energy Conversion
    network.add_edge(Conversion(network.get_node('Joule'), network.get_node('gram calorie'), lambda e: e / 4.184))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('Joule'), lambda e: e * 1000))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('kilowatt hour'), lambda e: e / 3600))
    network.add_edge(
        Conversion(network.get_node('Kilojoule'), network.get_node('British thermal Unit'), lambda e: e / 1.055))

    # power Conversion
    network.add_edge(Conversion(network.get_node('Horsepower'), network.get_node('Watt'), lambda e: e * 745.699872))

    # density Conversion
    network.add_edge(Conversion(network.get_node('API'), network.get_node('SgO'), lambda d: 141.5 / (131.5 + d)))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('API'), lambda d: 141.5 / d - 131.5))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('g/cc'), lambda d: d))
    network.add_edge(Conversion(network.get_node('SgW'), network.get_node('g/cc'), lambda d: d))
    network.add_edge(Conversion(network.get_node('SgG'), network.get_node('g/cc'), lambda d: d * StandardAirDensity))
    network.add_edge(Conversion(network.get_node('psia/ft'), network.get_node('lb/ft3'), lambda d: d * 144))
    network.add_edge(
        Conversion(network.get_node('g/cm3'), network.get_node('lb/ft3'), lambda d: d * 62.427960576144606))
    network.add_edge(Conversion(network.get_node('lb/ft3'), network.get_node('lb/stb'), lambda d: d * 5.614584))

    # viscosity conversions
    network.add_edge(Conversion(network.get_node('Pa*s'), network.get_node('Poise'), lambda v: v * 10))

    # data conversions
    network.add_edge(Conversion(network.get_node('byte'), network.get_node('bit'), lambda d: d * 8))
    network.add_edge(Conversion(network.get_node('byte'), network.get_node('B'), lambda d: d))
    network.add_edge(Conversion(network.get_node('bit'), network.get_node('b'), lambda d: d))

    for unit_kind in list(dictionary.keys()):
        if '_REVERSE' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                nameList = list(dictionary[unit_kind].keys())
            else:
                nameList = list(dictionary[unit_kind])
            # print(nameList)
            for unit_name in nameList:
                # print('R  2: ' + unit_name)
                for otherName in network.children_of(network.get_node(unit_name)):
                    # print('R   3: '+unit_name,otherName.getName())
                    if network.get_node(unit_name) != otherName:
                        network.add_edge(Conversion(otherName, network.get_node(unit_name),
                                                    network.edges[network.get_node(unit_name)][1][
                                                        network.edges[network.get_node(unit_name)][0].index(otherName)],
                                                    True))

    for unit_kind in list(dictionary.keys()):
        if '_FROMvolume' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            # if '_SI' in unit_kind and unit_kind.split('_')[0]  in SI_order[2] :
            for unit_name in list(dictionary[unit_kind]):
                # print('S  2: ' + unit_name)
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for otherName in network.children_of(network.get_node(unit_name.split('/')[0])):
                    if network.get_node(unit_name.split('/')[0]) != otherName:
                        print('R   3: ' + unit_name, otherName.get_name())
                        otherRate = otherName.get_name() + '/' + unit_name.split('/')[1]
                        network.add_node(UNode(otherRate))
                        network.add_edge(Conversion(network.get_node(unit_name), otherRate,
                                                    network.edges[network.get_node(unit_name.split('/')[1])][1][
                                                        network.edges[network.get_node(unit_name.split('/')[1])][
                                                            0].index(
                                                            otherName)]))
                        network.add_edge(Conversion(otherRate, network.get_node(unit_name),
                                                    network.edges[network.get_node(unit_name.split('/')[1])][1][
                                                        network.edges[network.get_node(unit_name.split('/')[1])][
                                                            0].index(
                                                            otherName)], True))

    to_remove = []
    for unit_kind in dictionary:
        if '_' in unit_kind:
            to_remove.append(unit_kind)
        else:  # if '_' not in unit_kind :
            dictionary[unit_kind] = tuple(dictionary[unit_kind])
    dictionary['userUnits'] = []

    for unit_kind in to_remove:
        dictionary.pop(unit_kind)

    return network


def _create_rates():
    # volumes / time
    rates = list(dictionary['rate']) if 'rate' in dictionary else []
    rates += [volume + '/' + time for volume in dictionary['volume'] for time in dictionary['time']]
    rates += [weight + '/' + time for weight in dictionary['weight'] for time in dictionary['time']]
    rates += [data + '/' + time for data in dictionary['dataBYTE'] for time in dictionary['time']]
    rates += [data + '/' + time for data in dictionary['dataBIT'] for time in dictionary['time']]
    dictionary['rate'] = tuple(set(rates))


def _create_volumeRatio():
    # volume / volume
    ratio = list(dictionary['volumeRatio']) if 'volumeRatio' in dictionary else []
    ratio += [numerator + '/' + denominator for numerator in dictionary['volume'] for denominator in
              dictionary['volume']]
    dictionary['volumeRatio'] = tuple(set(ratio))


def _create_density():
    # mass / volume
    density = list(dictionary['density']) if 'density' in dictionary else []
    density += [mass + '/' + volume for mass in dictionary['mass'] for volume in dictionary['volume']]
    dictionary['density'] = tuple(set(density))


def _create_speed():
    # length / time
    speed = list(dictionary['speed']) if 'speed' in dictionary else []
    speed += [length + '/' + time for length in dictionary['length'] for time in dictionary['time']]
    dictionary['speed'] = tuple(set(speed))


def _create_power():
    # length / time
    power = list(dictionary['power']) if 'power' in dictionary else []
    power += [energy + '/' + time for energy in dictionary['energy'] for time in dictionary['time']]
    dictionary['power'] = tuple(set(power))


def _create_productivityIndex():
    # volume / time / pressure
    productivityIndex = list(dictionary['productivityIndex']) if 'productivityIndex' in dictionary else []
    productivityIndex += [volume + '/' + time + '/' + pressure
                          for volume in dictionary['volume']
                          for time in dictionary['time']
                          for pressure in dictionary['pressure']]
    dictionary['productivityIndex'] = tuple(set(productivityIndex))


def _create_pressureGradient():
    # pressure / length
    pressureGradient = list(dictionary['pressureGradient']) if 'pressureGradient' in dictionary else []
    pressureGradient += [pressure + '/' + length for pressure in dictionary['pressure'] for length in
                         dictionary['length']]
    dictionary['pressureGradient'] = tuple(set(pressureGradient))


def _create_temperatureGradient():
    # pressure / length
    temperatureGradient = list(dictionary['temperatureGradient']) if 'temperatureGradient' in dictionary else []
    temperatureGradient += [temperature + '/' + length for temperature in dictionary['temperature'] for length in
                            dictionary['length']]
    dictionary['temperatureGradient'] = tuple(set(temperatureGradient))


def _create_acceleration():
    # length / time / time
    acceleration = list(dictionary['acceleration']) if 'acceleration' in dictionary else []
    acceleration += [(length + '/' + time1 + '2') if time1 == time2 else (length + '/' + time1 + '/' + time2)
                     for length in dictionary['length']
                     for time1 in dictionary['time']
                     for time2 in dictionary['time']]
    dictionary['acceleration'] = tuple(set(acceleration))


def rebuild_units():
    from .dictionaries import _load_dictionary
    dictionary, temperatureRatioConversions = _load_dictionary()
    unitsNetwork = _load_network()
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    return unitsNetwork, dictionary, temperatureRatioConversions


# load the network into an instance of the graph database
if not unyts_parameters_.reload_ and \
        isfile(dir_path + 'units/unitsNetwork.cache') and \
        isfile(dir_path + 'units/unitsDictionary.cache') and \
        isfile(dir_path + 'units/temperatureRatioConversions.cache'):
    try:
        with open(dir_path + 'units/unitsNetwork.cache', 'rb') as f:
            unitsNetwork = load(f)
        print('units network loaded from cache...')
        unyts_parameters_.reload_ = False
        unyts_parameters_.save_params()
    except:
        unitsNetwork, dictionary, temperatureRatioConversions = rebuild_units()
else:
    try:
        unitsNetwork = _load_network()
        # load the dictionary with ratio unis
        _create_rates()
        _create_volumeRatio()
        _create_density()
        _create_speed()
        _create_productivityIndex()
        _create_pressureGradient()
        _create_temperatureGradient()
        _create_power()
        unyts_parameters_.reload_ = False
        unyts_parameters_.save_params()
    except:
        unitsNetwork, dictionary, temperatureRatioConversions = rebuild_units()
    if unyts_parameters_.cache_:
        print('saving units network and dictionary to cache...')
        with open(dir_path + 'units/unitsNetwork.cache', 'wb') as f:
            dump(unitsNetwork, f)
        with open(dir_path + 'units/unitsDictionary.cache', 'w') as f:
            jdump(dictionary, f)


def network2frame():
    from pandas import DataFrame
    frame = DataFrame(data={}, columns=['source', 'target', 'lambda'])

    i = 0
    for node in unitsNetwork.edges:
        for children in unitsNetwork.children_of(node):
            frame.loc[i, ['source', 'target', 'lambda']] = [node.get_name(), children.get_name(),
                                                            unitsNetwork.conversion(node, children)]
            i += 1

    return frame.drop_duplicates(['source', 'target'])
