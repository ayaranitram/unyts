from unyts.network import UDigraph, UNode

g = UDigraph()
print('initial nodes', list(g.edges.keys()))
a = UNode('nanosecond')
g.add_node(a)
try:
    g.add_node(UNode('nanosecond'))
    print('no error when adding duplicate')
except Exception as e:
    print('error:', e)
print('nodes after', [n.get_name() for n in g.edges])
