import unyts.dictionaries as d

print('Pressure length', len(d.dictionary.get('Pressure', [])))
for u in d.dictionary.get('Pressure', []):
    if 'pod' in u.lower() or 'league2' in u.lower() or 'PODSS' in u:
        print('found', repr(u))