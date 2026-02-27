import sys
path=sys.argv[1]
start=int(sys.argv[2]); end=int(sys.argv[3])
with open(path) as f:
    for i,l in enumerate(f,1):
        if start<=i<=end:
            print(f"{i:4d}: {l.rstrip()}")
