#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:36:48 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
import logging
import os.path
from .parameters import unyts_parameters_, dir_path

try:
    from cloudpickle import dump as cloudpickle_dump, load as cloudpickle_load
    _cloudpickle_ = True
except ModuleNotFoundError:
    _cloudpickle_ = False


__version__ = '0.4.9'
__release__ = 20230127
__all__ = ['UNode', 'UDigraph', 'Conversion']


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
        self.print = False
        self._cloudpickle_ = _cloudpickle_
        if unyts_parameters_.cache_:
            self.load_memory()

    def save_memory(self, path=None) -> None:
        if path is None:
            path = dir_path + 'units/search_memory.cache'
        if self._cloudpickle_:
            print('saving search memory to cache...')
            with open(path, 'wb') as f:
                cloudpickle_dump(self.memory, f)
        else:
            logging.warning("Missing `cloudpickle` package. Not able to cache search memory.")

    def load_memory(self, path=None) -> None:
        if path is None:
            path = dir_path + 'units/search_memory.cache'
        if self._cloudpickle_ and os.path.isfile(dir_path + 'units/search_memory.cache'):
            try:
                print('loading search memory from cache...')
                with open(path, 'wb') as f:
                    cached_memory = cloudpickle_load(f)
                    self.memory.update(cached_memory)
            except:
                print('not able to load memory from cache.')
        elif not self._cloudpickle_:
            logging.warning("Missing `cloudpickle` package. Not able to cache search memory.")

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
        result = [n for n in self.edges if n.get_name() == name]
        if len(result) == 0:
            raise NameError(name)
        else:
            return result[0]

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

    def __str__(self) -> str:
        result = ''
        for src in self.edges:
            for dest in self.edges[src]:
                result = result + src.get_name() + '->' \
                         + dest.get_name() + \
                         str(self.conv) + '\n'
        return result[:-1]  # remove final \n

    def set_fvf(self, FVF) -> None:
        if type(FVF) is str:
            try:
                FVF = float(FVF)
            except ValueError:
                print('received FVF value is not a number: ' + str(FVF))
        if type(FVF) in (int, float):
            if FVF <= 0:
                logging.warning('FVF should be a positive number...')
            self.fvf = FVF

    def get_fvf(self):
        def valid_fvf(FVF):
            if type(FVF) is str:
                try:
                    FVF = float(FVF)
                except ValueError:
                    return False
            if type(FVF) in (int, float):
                if FVF <= 0:
                    return False
                else:
                    return FVF
            else:
                return False

        if self.fvf is None:
            print('Please enter formation Volume factor (FVF) in reservoir_volume/standard_volume:')
            while self.fvf is None:
                self.fvf = input(' FVF (rV/stV) = ')
                if not valid_fvf(self.fvf):
                    self.fvf = None
                else:
                    self.fvf = valid_fvf(self.fvf)
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
            return lambda x: x / self.conv(1)
        else:
            return self.conv

    def __str__(self) -> str:
        return self.src.get_name() + '->' + self.dest.get_name()
