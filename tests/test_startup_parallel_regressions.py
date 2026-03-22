# -*- coding: utf-8 -*-
"""Regression tests for startup staged parallel orchestration."""

from concurrent.futures import Future


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
