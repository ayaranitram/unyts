#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 17:52:34 2020

@author: martin
"""

__all__ = ['BFS']
__version__ = '0.1.0'
__release__ = 20220524


def BFS(graph, start, end, toPrint=False):
    """Assumes graph is a Digraph; start and end are nodes
        Returns a shortest path from start to end in graph"""
    initPath = [start]
    pathQueue = [initPath]
    visited = []
    while len(pathQueue) != 0:
        #Get and remove oldest element in pathQueue
        tmpPath = pathQueue.pop(0)
        if tmpPath in visited :
            if toPrint:
                print(' <UnitsConv> ' + str(len(pathQueue)) + ' paths in queue. ' + 'Already visited BFS path:\n', printPath(tmpPath))
        else :
            if toPrint:
                print(' <UnitsConv> ' + str(len(pathQueue)) + ' paths in queue. ' + 'Current BFS path:\n', printPath(tmpPath))
            lastNode = tmpPath[-1]
            if lastNode == end:
                return tmpPath
            for nextNode in graph.childrenOf(lastNode):
                if nextNode not in tmpPath:
                    newPath = tmpPath + [nextNode]
                    pathQueue.append(newPath)
            visited.append(tmpPath)
    return None


def printPath(path):
    """Assumes path is a list of nodes"""
    result = '  '
    if len(path) == 1 :
        result = result + str(path[0]) + ' = ' + str(path[0])
    else :
        for i in range(len(path)):
            if type(path[i]) == str :
                result = result + ' ' +  path[i] + ' '
            else:
                result = result + str(path[i])
                if i != len(path) - 1:
                    result = result + ' ' + chr(11157) + ' '
    return result