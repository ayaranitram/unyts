import json
import os
import pytest
from unyts import parameters
from unyts.parameters import unyts_parameters_, ini_path, ini_backup


def test_toggle_flags(tmp_path, monkeypatch, caplog):
    # redirect ini files to temporary directory
    monkeypatch.setattr(parameters, 'ini_path', tmp_path / 'params.json')
    monkeypatch.setattr(parameters, 'ini_backup', tmp_path / 'params.bak')
    # force reload to reinitialize using temp path
    unyts_parameters_.load_params()

    # initial default values
    assert unyts_parameters_.print_path_ is False
    parameters.print_path()
    assert unyts_parameters_.print_path_ is True
    parameters.print_path('off')
    assert unyts_parameters_.print_path_ is False

    parameters.cache(True)
    assert unyts_parameters_.cache_ is True
    parameters.cache('false')
    assert unyts_parameters_.cache_ is False

    parameters.raise_error(False)
    assert unyts_parameters_.raise_error_ is False
    parameters.raise_error('on')
    assert unyts_parameters_.raise_error_ is True

    parameters.verbose(1)
    assert unyts_parameters_.verbose_ is True
    assert unyts_parameters_.verbose_details_ == 1
    parameters.verbose(0)
    assert unyts_parameters_.verbose_ is False


def test_recursion_and_generation_limits(caplog):
    # recursion_limit returns and sets appropriately
    old = unyts_parameters_.max_recursion_
    assert parameters.recursion_limit() == old
    assert parameters.recursion_limit(5) == 5
    assert unyts_parameters_.max_recursion_ == 5
    with pytest.raises(ValueError):
        parameters.recursion_limit('bad')
    parameters.recursion_limit(12)  # reset to default for other tests

    oldg = unyts_parameters_.max_generations_
    assert unyts_parameters_.generations_limit() == oldg
    assert unyts_parameters_.generations_limit(10) == 10
    with pytest.raises(ValueError):
        unyts_parameters_.generations_limit('bad')
    unyts_parameters_.generations_limit(25)  # reset to default for other tests

def test_algorithm_setting(caplog):
    # valid algorithm sets value and adds warning
    unyts_parameters_.verbose_ = True
    unyts_parameters_.set_algorithm('BFS')
    assert unyts_parameters_.algorithm_ == 'BFS'
    # invalid algorithm does not change
    unyts_parameters_.set_algorithm('XYZ')
    assert unyts_parameters_.algorithm_ == 'BFS'


def test_parallel_setting(caplog):
    unyts_parameters_.set_parallel(None)
    assert unyts_parameters_.parallel_ is True
    unyts_parameters_.set_parallel(False)
    assert unyts_parameters_.parallel_ is False
    unyts_parameters_.set_parallel('threading')
    assert unyts_parameters_.parallel_ and unyts_parameters_.threading_
    with pytest.raises(ValueError):
        unyts_parameters_.set_parallel(123)


def test_timeout_and_is_intime():
    unyts_parameters_.set_timeout(1)
    assert unyts_parameters_.get_timeout() == 1
    with pytest.raises(TypeError):
        unyts_parameters_.set_timeout('bad')
    unyts_parameters_.reset_start_time()
    assert unyts_parameters_.is_intime() is True
    # simulate passing of time by manipulating _start_time
    unyts_parameters_._start_time -= 2
    assert unyts_parameters_.is_intime() is False
    unyts_parameters_.set_timeout(30)  # reset to longer timeout for other tests


def test_user_folder(tmp_path):
    unyts_parameters_.set_user_folder(tmp_path.as_posix())
    assert unyts_parameters_.get_user_folder().startswith(tmp_path.as_posix())
    # nonexistent should not change
    before = unyts_parameters_.get_user_folder()
    unyts_parameters_.set_user_folder(str(tmp_path / 'doesnotexist'))
    assert unyts_parameters_.get_user_folder() == before
