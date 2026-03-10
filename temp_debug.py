import os
from unyts.database import delete_cache
from unyts.parameters import unyts_parameters_
for f in ('units_dictionary.cache','units_network.cache'):
    p=unyts_parameters_.get_user_folder()+f
    if os.path.exists(p):
        os.remove(p)

import importlib
import unyts.dictionaries as dm
importlib.reload(dm)
from unyts.dictionaries import dictionary, collect_alias_conflicts
print('dict len', len(dictionary))
print('some volume keys', [k for k in dictionary if 'Volume' in k][:10])
conf=collect_alias_conflicts(dictionary)
print('conflict count', len(conf))
print('rm3 in conflicts?', 'rm3' in conf)
if 'rm3' in conf:
    print(conf['rm3'])
