from unyts.dictionaries import dictionary
print('initial has', 'dataBYTE' in dictionary)
from unyts import convert
print('after first convert import, has dataBYTE?', 'dataBYTE' in dictionary)
from unyts.database import _load_network
print('about to rebuild network second time...')
try:
    _load_network()
    print('second build succeeded, has dataBYTE?', 'dataBYTE' in dictionary)
except Exception as e:
    print('second build error', e)
    print('dictionary keys', list(dictionary.keys())[:20])
