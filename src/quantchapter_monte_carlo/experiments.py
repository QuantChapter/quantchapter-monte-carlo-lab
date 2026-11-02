"""Prespecified sample sizes and distinct seeded replications, without path selection."""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .core import MAX_SAMPLES, _finite, _integer, integrate

MAX_EVALUATIONS = 10_000_000


@dataclass(frozen=True)
class ConvergencePoint:
    """Across-replication summaries for one prescribed sample count."""

    samples: int
    replications: int
    root_mean_squared_error: float
    mean_standard_error: float
    empirical_coverage: float


def convergence_experiment(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    exact: float,
    sample_sizes: Iterable[int] = (100, 400, 1600, 6400),
    replications: int = 80,
    seed: int = 0,
    confidence: float = 0.95,
) -> tuple[ConvergencePoint, ...]:
    """Compare every prescribed sample size against a supplied analytic integral.

    Each size/replication receives a distinct consecutive integer seed. These
    pseudorandom streams approximate independent replications; no output or seed
    is selected after looking at errors. Total work is limited to ten million
    integrand evaluations. Empirical coverage is a finite simulation proportion,
    not proof of the nominal confidence level. Sizes must increase strictly.
    """
    truth = _finite(exact, "exact")
    repeats = _integer(replications, "replications", minimum=2, maximum=1000)
    start_seed = _integer(seed, "seed", minimum=0)
    sizes: list[int] = []
    total_work = 0
    try:
        for supplied_size in sample_sizes:
            size = _integer(supplied_size, "sample size", minimum=2, maximum=MAX_SAMPLES)
            if sizes and size <= sizes[-1]:
                raise ValueError("sample_sizes must be nonempty and strictly increasing")
            total_work += size * repeats
            if total_work > MAX_EVALUATIONS:
                raise ValueError("experiment exceeds the ten million evaluation limit")
            sizes.append(size)
    except TypeError as exc:
        raise ValueError("sample_sizes must be an iterable of integers") from exc
    if not sizes:
        raise ValueError("sample_sizes must be nonempty and strictly increasing")
    summaries = []
    for size_index, size in enumerate(sizes):
        results = [
            integrate(
                function,
                lower,
                upper,
                samples=size,
                seed=start_seed + size_index * repeats + replication,
                confidence=confidence,
            )
            for replication in range(repeats)
        ]
        errors = [result.estimate - truth for result in results]
        rmse = math.hypot(*(error / math.sqrt(repeats) for error in errors))
        if not math.isfinite(rmse):
            raise ValueError("replication errors are not representable as finite floats")
        mean_error = statistics.mean(result.standard_error for result in results)
        covered = sum(
            result.confidence_low <= truth <= result.confidence_high for result in results
        )
        summaries.append(ConvergencePoint(size, repeats, rmse, mean_error, covered / repeats))
    return tuple(summaries)
