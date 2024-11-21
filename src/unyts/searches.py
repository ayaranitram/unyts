#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 17:52:34 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.6.2'
__release__ = 20241121
__all__ = ['BFS', 'lean_BFS', 'DFS', 'print_path']

import logging
from unyts import unyts_parameters_


def BFS(graph, start, end, verbose=False) -> list:
    """
    Implementation of Breadth-First Search algorithm.
    Assumes graph is a digraph; `start` and `end` are nodes in the graph network.
    Returns a shortest path from `start` to `end` in graph.

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
    visited = list()
    while len(path_queue) != 0:
        # get and remove oldest element in path_queue
        conv_path = path_queue.pop(0)
        if conv_path in visited:
            if verbose:
                logging.info(f"""<BFS>: {len(path_queue)} paths in queue. Already visited BFS path:\n{print_path(conv_path)}""")
        else:
            if verbose:
                logging.info(f"""<BFS> {len(path_queue)} paths in queue. Current BFS path:\n{print_path(conv_path)}""")
            last_node = conv_path[-1]
            if last_node is end:
                if verbose:
                    logging.info(f"""<BFS> Found end node {end.get_name()} in the path:\n{print_path(conv_path)}""")
                return conv_path
            path_queue += [conv_path + [next_node]
                           for next_node in graph.children_of(last_node) 
                           if next_node not in conv_path]
            visited.append(conv_path)


def DFS(graph, start, end, verbose=False, branch_depht=25) -> list:
    """
    Implementation of Depth-First Search algorithm.
    Assumes graph is a digraph; `start` and `end` are nodes in the graph network.
    Returns a first found path from `start` to `end` in graph.

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
    from unyts.converter import _get_descendants
    branch_depht = unyts_parameters_.generations_limit() if branch_depht is None else branch_depht
    def dfs_(graph, node, visited, path_queue):
        visited.add(node)
        for child in graph.children_of(node):
            this_path = []
            if child in visited:
                continue
            if end.get_name() not in _get_descendants(child.get_name(), branch_depht):
                continue
            else:
                this_path.append(child)
                if child is end:
                    return path_queue + this_path
                else:
                    this_path = dfs_(graph, child, visited, this_path)
                    if end in this_path:
                        path_queue += this_path
                        break
        return path_queue
    path_queue = [start]
    visited = set()
    path_queue = dfs_(graph, start, visited, path_queue)
    if end in path_queue:
        return path_queue


class SlimUDigraph(object):
    """
    A simplified class, from the UDgraph class, to store a slimmed digraph dictionary containing only units related to the start and end of the search.
    The `edges` attribute is a dict mapping each node to a list of its children.
    The `children_of` method returns the list of nodes with direct relation to the key node. This method will be used by the search algorithms.
    """
    def __init__(self, edges:dict={}):
        self.edges = edges

    def children_of(self, node):
        return self.edges[node][0] if node in self.edges else []


def lean_BFS(graph, start, end, verbose=False, max_generations_screening=25) -> list:
    """
    Runs BFS algorithm on a lean digraph network, where only the nodes related to the `start` and `end` nodes are kept.
    Assumes graph is a digraph; `start` and `end` are nodes in the graph network.
    Returns a shortest path from `start` to `end` in graph.

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
    from unyts.converter import _get_descendants
    max_generations_screening = unyts_parameters_.generations_limit() if max_generations_screening is None else max_generations_screening
    generations_list = [g for g in [0, 1, 2, 3, 4, 5, 7, 10, 13, 16, 20, 25, 30, 40, 50] if g < max_generations_screening] + [max_generations_screening]
    selection = set()
    for generations in generations_list:
        generations += 1
        start_descendants = _get_descendants(start.get_name(), generations)
        end_descendants = _get_descendants(end.get_name(), generations)
        selection = start_descendants.intersection(end_descendants)
        if len(selection) > 0:
            break
    selection = selection.union({node for each in selection for node in _get_descendants(each, generations, get_combinations=False)})
    selected_edges = {k: v for k, v in graph.edges.items() if k.get_name() in selection}
    if len(selected_edges) > 0:
        if verbose:
            logging.info(f"<lean BFS> search graph slimmed from {len(graph.edges)} to {len(selected_edges)} nodes, in {generations} generations.")
        slim_graph = SlimUDigraph(selected_edges)
        return BFS(slim_graph, start, end, verbose=verbose and unyts_parameters_.verbose_details_ > 0)


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
