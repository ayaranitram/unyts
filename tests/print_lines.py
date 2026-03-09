import pathlib
p=pathlib.Path(r'D:\git\unyts\tests\test_ambiguous_aliases.py')
for i,line in enumerate(p.read_text().splitlines(),1):
    if 85 <= i <= 110:
        print(f"{i:3}: {line!r}")
    # else: skip large output
