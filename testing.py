# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:19:51 2021

@author: MCARAYA
"""

from units import convert
from units._database import unitsNetwork
convert(1,'cm3','m3')
convert(1000,'l','m3')
convert(1000,'cm3','l')
convert(1000,'ml','l')
