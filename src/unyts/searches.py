#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 17:52:34 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['BFS', 'print_path']


def BFS(graph, start, end, to_print=False) -> None:
    """Assumes graph is a Digraph; start and end are nodes
        Returns a shortest path from start to end in graph"""
    init_path = [start]
    path_queue = [init_path]
    visited = []
    while len(path_queue) != 0:
        # get and remove oldest element in path_queue
        tmp_path = path_queue.pop(0)
        if tmp_path in visited:
            if to_print:
                print('<UnitsConv> ' + str(len(path_queue)) + ' paths in queue. ' + 'Already visited BFS path:\n', print_path(tmp_path))
        else:
            if to_print:
                print('<UnitsConv> ' + str(len(path_queue)) + ' paths in queue. ' + 'Current BFS path:\n', print_path(tmp_path))
            last_node = tmp_path[-1]
            if last_node == end:
                return tmp_path
            for nextNode in graph.children_of(last_node):
                if nextNode not in tmp_path:
                    new_path = tmp_path + [nextNode]
                    path_queue.append(new_path)
            visited.append(tmp_path)


def print_path(path) -> str:
    """Assumes path is a list of nodes"""
    result = '  '
    if len(path) == 1:
        result = result + str(path[0]) + ' = ' + str(path[0])
    else:
        for i in range(len(path)):
            if type(path[i]) is str:
                result = result + ' ' + path[i] + ' '
            else:
                result = result + str(path[i])
                if i != len(path) - 1:
                    result = result + ' ' + chr(11157) + ' '
    return result
