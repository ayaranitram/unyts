#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:36:48 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
import logging
import os
from os.path import isfile

from .errors import NoFVFError
from .parameters import unyts_parameters_
from .helpers.logger import logger

try:
    from cloudpickle import dump as cloudpickle_dump, load as cloudpickle_load
    _cloudpickle_ = True
except ModuleNotFoundError:
    _cloudpickle_ = False


__version__ = '0.4.25'
__release__ = 20260225
__all__ = ['UNode', 'UDigraph', 'Conversion']


class UNode(object):
    """A class to represent a node in the units network graph. The `name` attribute is used for equality and hashing, so that nodes created in different sessions or after a rebuild compare equal; this allows memory caching and dictionary lookups to function across reloads."""
    __slots__ = ('name',)

    def __init__(self, name):
        """Initialize a UNode with a name string."""
        self.name = name if type(name) is str else ''

    def get_name(self):
        """Return the name of the UNode."""
        return self.name

    def __str__(self):
        """Return the string representation of the UNode."""
        return self.name

    # equality is based on the node name so that nodes created in different
    # sessions or after a rebuild compare equal; this allows memory caching
    # and dictionary lookups to function across reloads.
    def __eq__(self, other):
        """Return True if the UNode is equal to another UNode."""
        if not isinstance(other, UNode):
            return False
        return self.name == other.name

    def __hash__(self):
        """Return the hash of the UNode's name."""
        # needed for using nodes as dict keys
        return hash(self.name)


class UDigraph(object):
    """
    A class to store the digraph containing the units network and methods to facilitate its use.
    The `edges` attribute is a dict mapping each node to a list of its children
    The `children_of` method returns the list of nodes with direct relation to the key node. This method will be used by the search algorithms.
    """
    __slots__ = ('edges', '_edges_str', 'previous', 'recursion_limit', 'fvf', 'memory', 'print', '_cloudpickle_')

    def __init__(self) -> None:
        """Initialize a UDigraph with default attributes."""
        self.edges = {}
        self._edges_str = None
        self.previous = [(None, None)]
        self.recursion_limit = 5
        self.fvf = None
        self.memory = {}
        self.print = False
        self._cloudpickle_ = _cloudpickle_
        # do not load the search memory here, wait until the network is built
        # if unyts_parameters_.cache_ and unyts_parameters_.memory_:
        #     self.load_memory()

    def get_edges_str(self) -> dict:
        """Return a string representation of the edges in the UDigraph."""
        if self._edges_str is None:
            self._edges_str = {str(k): {str(each) for each in v[0]} for k, v in self.edges.items()}
        return self._edges_str

    def save_memory(self, path=None) -> None:
        """Save the current search memory to a cache file."""
        if path is None:
            path = unyts_parameters_.get_user_folder() + 'search_memory.cache'
        if self._cloudpickle_:
            logger.info('saving search memory to cache...')
            with open(path, 'wb') as f:
                cloudpickle_dump(self.memory, f)
        else:
            logger.warning("Missing `cloudpickle` package. Not able to cache search memory.")

    def load_memory(self, path=None) -> None:
        """Load search memory from a cache file."""
        if path is None:
            path = unyts_parameters_.get_user_folder() + 'search_memory.cache'
        if not self._cloudpickle_:
            logger.warning("Missing `cloudpickle` package. Not able to cache search memory.")

        # use the supplied path when checking for existence; previous
        # implementations looked at the default location regardless of the
        # argument, which meant callers providing an explicit file never
        # actually loaded it.
        if not isfile(path):
            msg = "starting clean memory..."
            logger.info(msg)
        else:
            logger.info('loading memory from cache...')
            try:
                with open(path, 'rb') as f:
                    cached_memory = cloudpickle_load(f)
                    # if a graph already exists, drop entries whose source
                    # node is not present (stale data); this makes it safe to
                    # load memory early and then build the graph without
                    # carrying dead references.
                    #if self.edges:
                    #     filtered = {k: v for k, v in cached_memory.items() if k in self.edges}
                    #     self.memory.update(filtered)
                    self.memory.update(cached_memory)
                    # else:
                        # don't populate until we have nodes; keep the cache
                        # around for a later load.
                    #     msg = "starting clean memory..."
                    #     logger.info(msg)
                    # report how many entries we kept (note that ``msg`` may
                    # have been reassigned above, so recompute it here)
                    msg = f"{len(self.memory)} conversion path{'' if len(self.memory) == 1 else 's'} in memory."
                    logger.info(msg)
            except Exception:
                msg = 'Failed to load memory from cache.'
                logger.warning(msg)
                try:
                    # os.remove(path)
                    msg = "starting clean memory..."
                    logger.info(msg)
                except Exception:
                    msg = f'The search cache file seems to be corrupted. Please delete it from: {path}'
                    logger.warning(msg)
        unyts_parameters_.last_path_str = msg

    def clean_memory(self):
        """Clean the search memory of the UDigraph."""
        self.memory = {}
        self.previous = [(None, None)]
        msg = f"memory cleaned."
        if unyts_parameters_.verbose_:
            logger.info(msg)

    def add_node(self, node) -> None:
        """Add a node to the UDigraph if it does not already exist."""
        # nodes may appear multiple times during the various dictionary
        # preprocessing branches.  earlier versions raised a ValueError so
        # that inconsistent dictionaries would fail fast, but the build
        # logic itself often generates the same unit in more than one
        # pass (e.g. nanosecond is added when handling `Time` and again
        # during plural/uppercase conversions).  the duplicate is harmless
        # so simply ignore it and optionally log a debug message.
        if node in self.edges:
            # don't spam the user in normal operation; only log when
            # verbosity/debugging is requested
            if unyts_parameters_.verbose_:
                logger.debug(f"skipping duplicate node {node}")
            return
        self.edges[node] = [], []

    def add_edge(self, edge, reverse=False) -> None:
        """Add an edge to the UDigraph."""
        src = edge.get_source()
        dest = edge.get_destination()
        conv = edge.get_convert()
        if not (src in self.edges and dest in self.edges):
            raise ValueError('Node not in graph')
        if dest not in self.edges[src][0]:  # avoid duplication
            self.edges[src][0].append(dest)
            self.edges[src][1].append(conv)

    def children_of(self, node):
        """Return the list of child nodes for a given node in the UDigraph."""
        return self.edges[node][0]

    def has_node(self, node):
        """Return True if a node exists in the UDigraph."""
        if type(node) is str:
            return node in [n.get_name() for n in self.edges]
        else:
            return node in self.edges

    def get_node(self, name):
        """Return the node with the given name from the UDigraph."""
        result = [n for n in self.edges if n.get_name() == name]
        if len(result) == 0:
            raise NameError(name)
        else:
            return result[0]

    def list_nodes(self):
        """Return a list of all node names in the UDigraph."""
        return list(set([n.get_name() for n in self.edges.keys()]))

    def convert(self, value, src, dest):
        """Convert a value from one unit to another in the UDigraph."""
        if type(src) != UNode:
            src = self.get_node(src)
        if type(dest) != UNode:
            dest = self.get_node(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)](value)

    def conversion(self, src, dest):
        """Return the conversion function from one unit to another in the UDigraph."""
        if type(src) != UNode:
            src = self.get_node(src)
        if type(dest) != UNode:
            dest = self.get_node(dest)
        return self.edges[src][1][self.edges[src][0].index(dest)]

    def __str__(self) -> str:
        """Return a string representation of the UDigraph.

        The original implementation iterated over ``self.edges[src]`` which
        is a pair ``[neighbors, conversions]`` and therefore produced
        ``list`` objects in place of destination nodes.  That resulted in
        ``AttributeError`` when converting to strings and made the repr
        unusable in tests.  We now explicitly iterate the node list only and
        drop the unused ``self.conv`` attribute entirely.
        """
        result_lines = []
        for src, (dests, _) in self.edges.items():
            for dest in dests:
                result_lines.append(f"{src.get_name()}->{dest.get_name()}")
        return "\n".join(result_lines)

    def set_fvf(self, FVF) -> None:
        """Set the Formation Volume Factor (FVF) for the UDigraph."""
        if type(FVF) is str:
            try:
                FVF = float(FVF)
            except ValueError:
                logger.error(f'received FVF value is not a number: {FVF}')
                raise TypeError(f'received FVF value is not a number: {FVF}')
        if type(FVF) in (int, float):
            if FVF <= 0:
                logger.error('FVF should be a positive number...')
                raise ValueError('FVF should be a positive number...')
            self.fvf = FVF

    def get_fvf(self) -> float:
        """Return the Formation Volume Factor (FVF) of the UDigraph."""
        def valid_fvf(FVF):
            """Return a valid FVF value or False if invalid."""
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
            if unyts_parameters_.gui:
                raise NoFVFError()
            else:
                print('Please enter formation Volume factor (FVF) in reservoir_volume/standard_volume:')
                while self.fvf is None:
                    self.fvf = input(' FVF (rV/stV) = ')
                    if not valid_fvf(self.fvf):
                        self.fvf = None
                    else:
                        self.fvf = valid_fvf(self.fvf)
        return self.fvf


class Conversion(object):
    """A class to represent a conversion between two units in the UDigraph, with an associated conversion function and metadata about whether it is a reverse or alias conversion."""
    __slots__ = ('src', 'dest', 'conv', 'rev', 'alias')

    def __init__(self, src, dest, conv, reverse=False, alias=False):
        """Assumes src and dest are nodes"""
        self.src = src
        self.dest = dest
        self.conv = conv
        self.rev = reverse
        self.alias = alias

    def get_source(self):
        """Return the source node of the conversion."""
        return self.src

    def get_destination(self):
        """Return the destination node of the conversion."""
        return self.dest

    def convert(self, value):
        """Convert a value using the conversion function."""
        return self.conv(value)

    def reverse(self, value):
        """Reverse a value using the conversion function."""
        return value / self.conv(1)

    def get_convert(self):
        """Return the conversion function for this conversion."""
        if self.rev and self.conv is not None:
            # return lambda x: x / self.conv(1)
            return self.reverse
        else:
            return self.conv

    def __str__(self) -> str:
        """Return a string representation of the conversion."""
        return self.src.get_name() + '->' + self.dest.get_name()
