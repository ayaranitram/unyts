#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 17:52:34 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.0'
__release__ = 20231222
__all__ = ['BFS', 'print_path']


def BFS(graph, start, end, verbose=False) -> list:
    """
    Assumes graph is a Digraph; start and end are nodes.
    Returns a shortest path from start to end in graph.

    Parameters
    ----------
    graph: Digraph
    start: node
    end: node
    verbose: bool
        to print or not print messages.
    Returns
    -------
    shortest_path: list
    """
    init_path = [start]
    path_queue = [init_path]
    visited = []
    while len(path_queue) != 0:
        # get and remove oldest element in path_queue
        conv_path = path_queue.pop(0)
        if conv_path in visited:
            if verbose:
                print(f"<UnitsConv> {len(path_queue)} paths in queue. Already visited BFS path:",
                      print_path(conv_path),
                      sep='\n')
        else:
            if verbose:
                print(f"<UnitsConv> {len(path_queue)} paths in queue. Current BFS path:",
                      print_path(conv_path),
                      sep='\n')
            last_node = conv_path[-1]
            if last_node is end:
                if verbose:
                    print(f"<UnitsConv> Found end node {end.get_name()} in the path:",
                          print_path(conv_path),
                          sep='\n')
                return conv_path
            path_queue += [conv_path + [next_node]
                           for next_node in graph.children_of(last_node) 
                           if next_node not in conv_path]
            visited.append(conv_path)


def print_path(path: list) -> str:
    """
    Assumes path is a list of nodes.

    Parameters
    ----------
    path: list
        a list of nodes
    Returns
    -------
    str
        string representation of list of nodes
    """
    result = '    '
    if len(path) == 1:
        result = f"{path[0]} = {path[0]}"
    else:
        for i in range(len(path)):
            if type(path[i]) is str and path[i] not in ['(1)', '(v)']:
                if result[-3:] == ' > ':
                    result = result[:-3]
                result = result + ' ' + path[i] + ' '
            elif type(path[i]) in (int, float, complex):
                result = result + str(path[i]) + ' '
            else:
                result = result + str(path[i])
                if i != len(path) - 1:
                    result = result + ' > '
    return result.strip()
