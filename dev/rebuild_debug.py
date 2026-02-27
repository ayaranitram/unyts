import os
from unyts.parameters import unyts_parameters_

# remove caches to force rebuild
for fname in ('search_memory.cache', 'units_network.cache', 'units_dictionary.cache',
              'temperature_ratio_conversions.cache', 'unitless_names.cache'):
    path = os.path.join(unyts_parameters_.get_user_folder(), fname)
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print('manual remove failed', path, e)

# reload modules to ensure fresh dictionary
import importlib
import unyts.dictionaries
# force fresh dictionary generation by calling loader directly
print('forcing fresh dictionary build via _load_dictionary')
dict_result = unyts.dictionaries._load_dictionary()
dictionary = dict_result[0]
print('fresh dictionary keys:', sorted(dictionary.keys()))
# inspect all keys containing '_PLURALwS' and their types
for k in sorted(dictionary):
    if '_PLURALwS' in k:
        v = dictionary[k]
        print(f"{k}: type={type(v)}, len={len(v) if hasattr(v, '__len__') else 'n/a'}")
        if isinstance(v, (list, tuple)):
            seen=set(); bad=[]
            for item in v:
                if item in seen:
                    bad.append(item)
                else:
                    seen.add(item)
            if bad:
                print('  duplicates inside value:', bad)

# then inspect specific known key
key = 'Time_PLURALwS_UPPER_REVERSE'
if key in dictionary:
    vals = dictionary[key]
    print(f"{key} has {len(vals)} items: {vals}")
    seen=set(); bad=[]
    for v in vals:
        if v in seen:
            bad.append(v)
        else:
            seen.add(v)
    print('duplicates in this list', bad)
else:
    print(key, 'not found in fresh dictionary')

# re-import database to provoke network building now that caches cleared
import unyts.database
importlib.reload(unyts.database)

try:
    net = unyts.database._load_network()
    print('network built successfully with', len(net.edges), 'nodes')
except Exception as e:
    import traceback
    traceback.print_exc()
