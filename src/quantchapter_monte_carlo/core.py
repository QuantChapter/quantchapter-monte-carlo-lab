"""A bounded, streaming estimator with a private pseudorandom stream."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from numbers import Real
from random import Random
from statistics import NormalDist

MAX_SAMPLES = 1_000_000


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number, excluding booleans")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be representable as a finite float") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _integer(value: int, name: str, *, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def _product(*values: float) -> float:
    """Multiply finite factors without avoidable intermediate overflow."""
    if any(value == 0 for value in values):
        return 0.0
    mantissa = 1.0
    exponent = 0
    for value in values:
        fraction, power = math.frexp(value)
        mantissa *= fraction
        exponent += power
    try:
        result = math.ldexp(mantissa, exponent)
    except OverflowError as exc:
        raise ValueError("result is not representable as a finite float") from exc
    if not math.isfinite(result) or result == 0:
        raise ValueError("nonzero result overflows or underflows floating-point representation")
    return result


@dataclass(frozen=True)
class IntegrationResult:
    """An estimate and its approximate normal interval; all values use integral units."""

    estimate: float
    standard_error: float
    confidence_level: float
    confidence_low: float
    confidence_high: float
    samples: int
    seed: int
    lower: float
    upper: float


def integrate(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    samples: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> IntegrationResult:
    """Estimate the integral of a bounded real function over [lower, upper].

    Each call owns Random(seed); global random state is untouched. Results are
    reproducible for a fixed supported interpreter/environment, not promised
    bit-for-bit across Python versions. The standard error uses sample variance
    (n-1 divisor). The interval is a CLT/normal approximation, not a finite-sample
    coverage guarantee. Boundedness and integrability are caller assumptions;
    only sampled values can be validated. Function exceptions propagate.

    At least two and at most one million samples are required. Bounds must be
    finite, ordered, and have a finite representable positive width. Arbitrary
    callables execute locally with the caller's privileges.
    """
    if not callable(function):
        raise ValueError("function must be callable")
    left = _finite(lower, "lower")
    right = _finite(upper, "upper")
    width = right - left
    if not math.isfinite(width) or width <= 0:
        raise ValueError("bounds must satisfy lower < upper with finite positive width")
    count = _integer(samples, "samples", minimum=2, maximum=MAX_SAMPLES)
    # Nonnegative integer seeds avoid cross-language sign-convention ambiguity.
    chosen_seed = _integer(seed, "seed", minimum=0)
    level = _finite(confidence, "confidence")
    if not 0 < level < 1:
        raise ValueError("confidence must lie strictly between 0 and 1")
    probability = 0.5 + level / 2
    if not 0.5 < probability < 1:
        raise ValueError("confidence is too close to an endpoint to represent its normal quantile")
    quantile = NormalDist().inv_cdf(probability)
    random = Random(chosen_seed)
    scale = 0.0
    mean = 0.0
    centered_sum = 0.0
    for index in range(1, count + 1):
        position = left + width * random.random()
        value = _finite(function(position), f"integrand result at sample {index}")
        magnitude = abs(value)
        if magnitude > scale:
            factor = scale / magnitude
            mean *= factor
            centered_sum *= factor * factor
            scale = magnitude
        normalized = value / scale if scale else 0.0
        difference = normalized - mean
        mean += difference / index
        centered_sum += difference * (normalized - mean)
    estimate = _product(width, scale, mean)
    normalized_standard_error = math.sqrt(max(0.0, centered_sum) / (count - 1) / count)
    standard_error = _product(width, scale, normalized_standard_error)
    radius = _product(quantile, standard_error)
    low = estimate - radius
    high = estimate + radius
    if not math.isfinite(low) or not math.isfinite(high):
        raise ValueError("confidence interval endpoints are not representable as finite floats")
    return IntegrationResult(
        estimate, standard_error, level, low, high, count, chosen_seed, left, right
    )
