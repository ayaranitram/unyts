import unyts.dictionaries as d

results = []
for k,v in d.dictionary.items():
    for u in v:
        if 'PODSS' in u or 'pods' in u.lower():
            results.append((k,u))
print(results)