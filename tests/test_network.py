import os
import tempfile
import pytest

from unyts.network import UNode, UDigraph, Conversion
from unyts.parameters import unyts_parameters_
from unyts.errors import NoFVFError


def test_unode_basics():
    n1 = UNode('meter')
    n2 = UNode('meter')
    n3 = UNode('ft')

    assert n1.get_name() == 'meter'
    assert str(n1) == 'meter'
    assert n1 == n2
    assert not (n1 != n2)
    assert hash(n1) == hash(n2)
    assert not (n1 == n3)
    assert not (n1 == object())


def test_udigraph_node_edge_operations(tmp_path):
    g = UDigraph()
    # initially empty
    assert not g.has_node('a')
    a = UNode('a')
    b = UNode('b')

    g.add_node(a)
    assert g.has_node(a)
    assert g.has_node('a')
    assert g.list_nodes() == ['a']
    # duplicate node does not crash
    g.add_node(a)

    with pytest.raises(NameError):
        g.get_node('doesnotexist')
    assert g.get_node('a') is a

    # cannot add edge before both nodes exist
    c = UNode('c')
    conv = Conversion(a, b, lambda x: x*2)
    with pytest.raises(ValueError):
        g.add_edge(conv)

    # add missing node and then edge
    g.add_node(b)
    g.add_edge(conv)
    assert g.children_of(a) == [b]
    # conversion from a to b
    assert g.convert(1, a, b) == 2
    assert g.convert(3, 'a', 'b') == 6
    fn = g.conversion('a', 'b')
    assert fn(5) == 10

    # __str__ has at least source->dest substring
    assert 'a->b' in str(g)


def test_fvf_set_get_and_errors(monkeypatch):
    g = UDigraph()
    # invalid types
    with pytest.raises(TypeError):
        g.set_fvf('not a number')
    with pytest.raises(ValueError):
        g.set_fvf(-1)
    g.set_fvf(1.5)
    assert g.get_fvf() == 1.5
    # string that converts to float is acceptable
    g.set_fvf('2.0')
    assert g.get_fvf() == 2.0
    # temporary invalid value triggers loop; monkeypatch input
    g2 = UDigraph()
    g2.fvf = None
    unyts_parameters_.gui = False
    # simulate user entering invalid then valid via monkeypatch
    inputs = iter(['-1', '0', '3'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    assert g2.get_fvf() == 3

    # when gui mode on and no fvf set -> raise NoFVFError
    g3 = UDigraph()
    g3.fvf = None
    unyts_parameters_.gui = True
    with pytest.raises(NoFVFError):
        g3.get_fvf()
    unyts_parameters_.gui = False


def test_memory_save_load(tmp_path, caplog):
    g = UDigraph()
    g.memory = {'foo': 1}
    cache_file = tmp_path / 'cache.bin'
    # saving when cloudpickle available: should not crash
    g.save_memory(path=str(cache_file))
    assert cache_file.exists()
    # load into new graph
    g2 = UDigraph()
    g2.load_memory(path=str(cache_file))
    assert g2.memory == {'foo': 1}

    # corrupt the file and ensure warnings are logged
    cache_file.write_text('not a pickle')
    caplog.set_level('WARNING', logger='Unyt')
    g2.load_memory(path=str(cache_file))
    assert 'Failed to load memory' in caplog.text or 'corrupted' in caplog.text


def test_clean_memory_logs(caplog):
    g = UDigraph()
    g.memory = {'a': 1}
    unyts_parameters_.verbose_ = True
    caplog.set_level('INFO', logger='Unyt')
    g.clean_memory()
    assert g.memory == {}
    assert 'memory cleaned' in caplog.text
    unyts_parameters_.verbose_ = False
