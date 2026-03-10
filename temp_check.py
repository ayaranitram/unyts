import os
from unyts.parameters import unyts_parameters_
for f in ('units_dictionary.cache','units_network.cache','temperature_ratio_conversions.cache','unitless_names.cache'):
    p = unyts_parameters_.get_user_folder() + f
    if os.path.exists(p):
        os.remove(p)
        print('removed',p)

import unyts
from unyts.dictionaries import _load_dictionary, collect_alias_conflicts
fresh,_,_ = _load_dictionary()
conf = collect_alias_conflicts(fresh)
print('pods count', len([u for u in fresh.get('Pressure',[]) if 'PODS' in u.upper()]))
print('sample', [u for u in fresh.get('Pressure',[]) if 'PODS' in u.upper()][:10])
