from unyts.database import delete_cache
from unyts.parameters import unyts_parameters_
import os, importlib

# remove caches
for f in ('units_dictionary.cache','units_network.cache'):
    p=unyts_parameters_.get_user_folder()+f
    if os.path.exists(p):
        os.remove(p)
        print('removed', p)

import unyts.dictionaries as dm
importlib.reload(dm)
from unyts.dictionaries import dictionary, collect_alias_conflicts

print('dictionary len', len(dictionary), 'type', type(dictionary))
print('has volume reverse dicts?')
for k,v in dictionary.items():
    if isinstance(v, dict) and 'reservoir cubic meter' in v:
        print('found in', k, v['reservoir cubic meter'])
conf=collect_alias_conflicts(dictionary)
print('rm3 conflict', conf.get('rm3'))
print('all conflicts sample', list(conf.items())[:20])
