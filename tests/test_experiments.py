"""Prespecified replication behavior and independent analytic calibration checks."""

from __future__ import annotations

import math
from itertools import count
from typing import Any

import pytest

from quantchapter_monte_carlo import convergence_experiment, integrate


def test_every_replication_uses_documented_distinct_seed_and_is_included() -> None:
    points = convergence_experiment(
        lambda x: x * x, 0, 1, exact=1 / 3, sample_sizes=(4, 16), replications=3, seed=20
    )
    for index, point in enumerate(points):
        runs = [
            integrate(lambda x: x * x, 0, 1, samples=point.samples, seed=20 + index * 3 + rep)
            for rep in range(3)
        ]
        errors = [run.estimate - 1 / 3 for run in runs]
        assert point.replications == 3
        assert point.root_mean_squared_error == pytest.approx(
            math.sqrt(sum(error**2 for error in errors) / 3)
        )
        assert point.mean_standard_error == pytest.approx(
            sum(run.standard_error for run in runs) / 3
        )
        assert (
            point.empirical_coverage
            == sum(run.confidence_low <= 1 / 3 <= run.confidence_high for run in runs) / 3
        )


def test_constant_function_has_zero_empirical_error_and_full_coverage() -> None:
    points = convergence_experiment(
        lambda _: 3.0, 2, 7, exact=15.0, sample_sizes=iter([2, 10]), replications=4
    )
    assert all(point.root_mean_squared_error == 0 for point in points)
    assert all(point.mean_standard_error == 0 for point in points)
    assert all(point.empirical_coverage == 1 for point in points)


def test_empirical_rmse_matches_analytic_scale_across_prespecified_replicates() -> None:
    points = convergence_experiment(
        lambda x: x * x,
        0,
        1,
        exact=1 / 3,
        sample_sizes=(64, 256, 1024),
        replications=150,
        seed=2026,
    )
    for point in points:
        theory = math.sqrt(4 / (45 * point.samples))
        assert 0.7 * theory < point.root_mean_squared_error < 1.3 * theory
        assert 0.8 <= point.empirical_coverage <= 1.0
    assert points[-1].root_mean_squared_error < points[0].root_mean_squared_error


@pytest.mark.parametrize("sizes", [[], [2, 2], [4, 2], [1], [True], [2.5], [1_000_001], None])
def test_invalid_sample_size_sequences_fail(sizes: Any) -> None:
    with pytest.raises(ValueError):
        convergence_experiment(lambda x: x, 0, 1, exact=0.5, sample_sizes=sizes)


@pytest.mark.parametrize("repeats", [0, 1, 1001, True, 2.5, "3"])
def test_replication_count_validation(repeats: Any) -> None:
    with pytest.raises(ValueError):
        convergence_experiment(lambda x: x, 0, 1, exact=0.5, replications=repeats)


def test_total_work_budget_is_checked_before_function_evaluation() -> None:
    def forbidden(_: float) -> float:
        raise AssertionError("work budget must be checked before evaluation")

    with pytest.raises(ValueError, match="ten million"):
        convergence_experiment(forbidden, 0, 1, exact=0, sample_sizes=[1_000_000], replications=11)


def test_unbounded_size_iterator_is_stopped_by_prefix_work_budget() -> None:
    with pytest.raises(ValueError, match="ten million"):
        convergence_experiment(lambda x: x, 0, 1, exact=0.5, sample_sizes=count(2))


def test_unrepresentable_reference_errors_fail() -> None:
    with pytest.raises(ValueError, match="replication errors"):
        convergence_experiment(lambda _: 1.7e308, 0, 1, exact=-1.7e308, sample_sizes=[2])


def test_rmse_avoids_intermediate_norm_overflow() -> None:
    points = convergence_experiment(
        lambda _: 1e308, 0, 1, exact=0, sample_sizes=[2], replications=80
    )
    assert points[0].root_mean_squared_error == pytest.approx(1e308)


@pytest.mark.parametrize("exact", [math.nan, math.inf, True, "1"])
def test_exact_reference_must_be_finite_number(exact: Any) -> None:
    with pytest.raises(ValueError):
        convergence_experiment(lambda x: x, 0, 1, exact=exact)
