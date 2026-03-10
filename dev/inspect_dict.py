from unyts import converter
from unyts.dictionaries import dictionary
print('len', len(dictionary))
print('sample', [(k, type(v)) for k,v in list(dictionary.items())[:20]])
print('dictvals', sum(1 for v in dictionary.values() if isinstance(v, dict)))
