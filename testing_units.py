#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:38:33 2020

@author: martin
"""

from units import *

a = lenght(3,'m')
b = lenght(4,'yd')
c = a*b
d = b*a

print(a,b)
print(a+b)
print(b+a)
print(1+a)
print(a+1)
print(a-b)
print(b-a)
print(1-a)
print(a-1)
print(-a)
print(a*b)
print(b*a)
print(2*a)
print(a*2)
print(a/b)
print(b/a)
print(2/a)
print(a/2)
print(c)
print(c*a)
print(c/b)
print( 2/a * a/2)


import units

v = units.units(100,'Km/h')
print(v.to('mi/h'))