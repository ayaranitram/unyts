from pathlib import Path
from unyts.network import UDigraph, UNode
import tempfile

cache_path = Path(tempfile.gettempdir()) / "test_search_memory.cache"
if cache_path.exists():
    cache_path.unlink()

# build first graph
print('building first graph')
g1 = UDigraph()
n1 = UNode('foo')
g1.add_node(n1)
g1.memory[n1] = {'dummy': 1}
g1.save_memory(str(cache_path))
print('saved cache at', cache_path, 'exists?', cache_path.exists())

# new graph g2
print('new graph g2, load before nodes')
g2 = UDigraph()
g2.load_memory(str(cache_path))
print('memory after first load', g2.memory)
print('edges before add', g2.edges)

print('adding node then reloading')
g2.add_node(UNode('foo'))
g2.load_memory(str(cache_path))
print('memory after second load', g2.memory)
