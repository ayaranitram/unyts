from unyts import *

t = isinstance(units(1, 'ft'), Unit)
print(t)


convert(3.6, 'km', 'yd')
units(1, 'ft')
t = units(1, 'ft') + units(6, 'in')
print(t)
