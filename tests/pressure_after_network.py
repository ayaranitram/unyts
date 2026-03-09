import unyts
import unyts.dictionaries as d
# import converter to force network build
import unyts.converter

print('Pressure entries after network build:')
for u in d.dictionary.get('Pressure', []):
    print(repr(u))
