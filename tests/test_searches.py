import pytest
from unyts.searches import (BFS, DFS, lean_BFS, hybrid_BFS, print_path,
                             SlimUDigraph, SerialRun, _bfs, _lean_bfs)
from unyts.network import UNode
from unyts.parameters import unyts_parameters_
from unyts.Empty import Empty


def make_simple_graph():
    # a -> b -> c
    a = UNode('a')
    b = UNode('b')
    c = UNode('c')
    edges = {a: ([b], []), b: ([c], []), c: ([], [])}
    return a, b, c, edges


def test_bfs_basic():
    a, b, c, edges = make_simple_graph()
    g = SlimUDigraph(edges)
    path = BFS(g, a, c)
    assert path == [a, b, c]
    # start == end returns [start]
    assert BFS(g, a, a) == [a]
    # no path returns None
    d = UNode('d')
    assert BFS(g, a, d) is None


def test_bfs_timeout(monkeypatch):
    # when is_intime returns False immediately
    monkeypatch.setattr(unyts_parameters_, 'is_intime', lambda: False)
    a, b, c, edges = make_simple_graph()
    g = SlimUDigraph(edges)
    assert BFS(g, a, c) == Empty
    # restore
    monkeypatch.setattr(unyts_parameters_, 'is_intime', lambda: True)


def test_dfs_basic(monkeypatch):
    a, b, c, edges = make_simple_graph()
    g = SlimUDigraph(edges)
    assert DFS(g, a, c) == [a, b, c]
    assert DFS(g, a, a) == [a]
    # if end unreachable
    d = UNode('d')
    assert DFS(g, a, d) is None
    # again simulate timeout
    monkeypatch.setattr(unyts_parameters_, 'is_intime', lambda: False)
    assert DFS(g, a, c) == Empty
    monkeypatch.setattr(unyts_parameters_, 'is_intime', lambda: True)


def test_print_path_various():
    assert print_path([UNode('x')]) == '    x = x'
    assert print_path(['a', 'b', 'c']) == 'a b c'
    assert print_path([1, '->', 2]) == '    1 -> 2'


def test_slim_and_lean(monkeypatch):
    # patch _get_descendants to simple identity
    import unyts.searches as searches
    monkeypatch.setattr(searches, '_get_descendants', lambda name, gen, get_combinations=True: {name})
    a, b, c, edges = make_simple_graph()
    # graph has path from a to c
    g = SlimUDigraph(edges)
    assert lean_BFS(g, a, c) == [a, b, c]
    # now if start and end have no common descendants, simulate
    monkeypatch.setattr(searches, '_get_descendants', lambda name, gen, get_combinations=True: set())
    assert lean_BFS(g, a, c) is None


def test_serialrun():
    # when results dict already contains a value, return it without calling
    called = False
    def target(x):
        nonlocal called
        called = True
        return x*2
    results = {'foo': 5}
    runner = SerialRun(target, (results, 3))
    assert runner.start() == 5
    assert not called
    # now empty results: call target
    results = {'foo': ''}
    runner = SerialRun(target, (results, 3))
    assert runner.start() == 6
    assert called


def test_parallel_helpers(monkeypatch):
    # _bfs and _lean_bfs should populate the results dictionary
    results = {'bfs': '', 'lean_bfs': ''}
    a, b, c, edges = make_simple_graph()
    g = SlimUDigraph(edges)
    _bfs(results, g, a, c)
    assert results['bfs'] == [a, b, c]
    results = {'bfs': '', 'lean_bfs': ''}
    _lean_bfs(results, g, a, c)
    assert results['lean_bfs'] == [a, b, c]


def test_hybrid_bfs_serial(monkeypatch):
    # disable parallel so SerialRun is used
    unyts_parameters_.parallel_ = False
    a, b, c, edges = make_simple_graph()
    g = SlimUDigraph(edges)
    path = hybrid_BFS(g, a, c)
    assert path == [a, b, c]
    unyts_parameters_.parallel_ = True  # restore default state
