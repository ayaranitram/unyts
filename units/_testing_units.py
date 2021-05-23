#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:38:33 2020

@author: martin
"""

from units import *

convert(1,'m','mm',True)
convert(1,'m','in',True)
convert(1,'g/cc','lb/ft3',True)

a = length(3,'m')
print(a,type(a))
b = length(4,'yd')
print(b,type(b))
c = a*b
print(c,type(c))
d = b*a
print(d,type(d))
e = a/b
print(e,type(e))
f = b/a
print(f,type(f))
g = c//b
print(g,type(g))
h = c//a
print(h,type(h))
i = -a
print(i,type(i))
j = abs(i)
print(j,type(j))
k = a*c
print(k,type(k))


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