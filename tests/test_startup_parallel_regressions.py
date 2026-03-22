# -*- coding: utf-8 -*-
"""Regression tests for startup staged parallel orchestration."""

from concurrent.futures import Future
import threading
import time
import os
import subprocess
import sys

import pytest


def test_staged_fallback_executes_each_function_once_on_parallel_failure():
    from unyts import database as db

    calls = {'stage_a': 0, 'stage_b': 0, 'complete': 0}

    def stage_a_fn():
        calls['stage_a'] += 1

    def stage_b_fn():
        calls['stage_b'] += 1

    def complete_fn():
        calls['complete'] += 1

    def failing_parallel(_functions):
        raise RuntimeError('forced failure')

    db._run_startup_create_stages(
        parallel_3_14=True,
        parallel_execute_fn=failing_parallel,
        stage_a=[stage_a_fn],
        stage_b=[stage_b_fn],
        complete_products_fn=complete_fn,
    )

    assert calls == {'stage_a': 1, 'stage_b': 1, 'complete': 1}


def test_parallel_execute_honors_startup_worker_cap(monkeypatch):
    from unyts.helpers import _parallel_helpers as ph

    captured = {'max_workers': None}

    class DummyExecutor:
        def __init__(self, max_workers):
            captured['max_workers'] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(self, fn):
            future = Future()
            try:
                future.set_result(fn())
            except Exception as exc:
                future.set_exception(exc)
            return future

    monkeypatch.setattr(ph, 'ThreadPoolExecutor', DummyExecutor)
    monkeypatch.setenv('UNYTS_STARTUP_MAX_WORKERS', '2')

    fns = [lambda: i for i in range(6)]
    ph.parallel_execute(fns)

    assert captured['max_workers'] == 2


def test_parallel_execute_explicit_max_workers_overrides_cap(monkeypatch):
    from unyts.helpers import _parallel_helpers as ph

    captured = {'max_workers': None}

    class DummyExecutor:
        def __init__(self, max_workers):
            captured['max_workers'] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(self, fn):
            future = Future()
            future.set_result(fn())
            return future

    monkeypatch.setattr(ph, 'ThreadPoolExecutor', DummyExecutor)
    monkeypatch.setenv('UNYTS_STARTUP_MAX_WORKERS', '1')

    fns = [lambda: i for i in range(5)]
    ph.parallel_execute(fns, max_workers=3)

    assert captured['max_workers'] == 3


def test_initialize_startup_build_runs_once_with_concurrent_calls(monkeypatch):
    from unyts import database as db

    calls = {'count': 0}

    def fake_run_startup(_parallel_enabled, _parallel_execute_fn):
        calls['count'] += 1
        time.sleep(0.05)

    monkeypatch.setattr(db, '_run_startup_create_stages', fake_run_startup)
    monkeypatch.setattr(db, '_STARTUP_INIT_DONE', False)
    monkeypatch.setattr(db, '_STARTUP_INIT_LOCK', threading.Lock())

    threads = [
        threading.Thread(target=db._initialize_startup_build, args=(False, lambda _fns: None))
        for _ in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert calls['count'] == 1
    assert db._STARTUP_INIT_DONE is True


def test_productivity_index_guard_skips_combinatorial_oom(monkeypatch):
    from unyts import database as db

    test_dictionary = {
        'Volume': tuple(f'v{i}' for i in range(1000)),
        'Time': tuple(f't{i}' for i in range(1000)),
        'Pressure': tuple(f'p{i}' for i in range(1000)),
        'ProductivityIndex': ('existing/unit',),
    }

    monkeypatch.setattr(db, 'dictionary', test_dictionary)
    monkeypatch.setenv('UNYTS_MAX_PRODUCTIVITY_INDEX_COMBINATIONS', '1000000')

    db._create_ProductivityIndex()

    assert db.dictionary['ProductivityIndex'] == ('existing/unit',)


@pytest.mark.skipif(
    os.environ.get('UNYTS_ENABLE_STRESS_SMOKE') != '1',
    reason='Set UNYTS_ENABLE_STRESS_SMOKE=1 to run startup stress smoke test.',
)
def test_python314_startup_stress_smoke_memory_budget():
    pytest.importorskip('psutil')

    max_rss_mb = int(os.environ.get('UNYTS_STRESS_MAX_RSS_MB', '6144'))
    loops = int(os.environ.get('UNYTS_STRESS_LOOPS', '200'))

    code = (
        "import psutil\n"
        "from unyts import convert\n"
        f"loops = {loops}\n"
        "for _ in range(loops):\n"
        "    convert(1.0, 'psi', 'bar')\n"
        "rss = psutil.Process().memory_info().rss\n"
        "print(rss)\n"
    )

    env = os.environ.copy()
    env.setdefault('UNYTS_PARALLEL_3_14', '0')
    proc = subprocess.run(
        [sys.executable, '-c', code],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    rss_bytes = int(proc.stdout.strip().splitlines()[-1])
    assert rss_bytes <= max_rss_mb * 1024 * 1024
