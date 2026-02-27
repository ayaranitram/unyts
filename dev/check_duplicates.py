from unyts.dictionaries import dictionary

dups = {}
for kind, vals in dictionary.items():
    if isinstance(vals, (list, tuple)):
        seen = set()
        for v in vals:
            if v in seen:
                dups.setdefault(kind, []).append(v)
            else:
                seen.add(v)

# write results to output file for easier capture
with open('dev/duplicates_out.txt', 'w', encoding='utf-8') as outf:
    outf.write('dictionary keys:\n')
    outf.write(str(sorted(dictionary.keys())) + '\n')
    outf.write('\nduplicate entries by category:\n')
    outf.write(str(dups) + '\n')
    key = 'Time_PLURALwS_UPPER_REVERSE'
    if key in dictionary:
        outf.write(f"\n{key} length: {len(dictionary[key])}\n")
        outf.write(str(dictionary[key]) + '\n')
        seen = set()
        bad = []
        for v in dictionary[key]:
            if v in seen:
                bad.append(v)
            else:
                seen.add(v)
        outf.write('duplicates in ' + key + ' ' + str(bad) + '\n')
    else:
        outf.write(f"{key} not present in dictionary\n")
