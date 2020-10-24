#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:46:04 2020

@author: martin
"""


def isUnit(Unit) :
    if type(Unit) is str :
        Unit = Unit.strip()
    for each in list(_unit.dictionary.keys()) :
        if '_' not in each :
            isU = Unit in list(_unit.dictionary[each])
            if isU :
                # print(" '" + Unit + "' is unit")
                return True
    
    if '/' in Unit or '*' in Unit:
        # print(" splitting '" + Unit + "'")
        UnitSplit = []
        for each in Unit.split('/') :
            UnitSplit += each.split('*')
        ret = [False]*len(UnitSplit)
        for each in list(_unit.dictionary.keys()) :
            if '_' not in each :
                for subU in range(len(UnitSplit)) :
                    if UnitSplit[subU] in list(_unit.dictionary[each]) :
                        ret[subU] = True
        # print(" split of '" + Unit + "' " + str(ret))
        for each in ret :
            if not each :
                return False
    # print(" finally '" + Unit + "' is unit")
    return True
    







