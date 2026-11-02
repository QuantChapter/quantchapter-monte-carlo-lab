"""Reference calculations, validation boundaries, and estimator invariants."""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantchapter_monte_carlo import integrate


def test_constant_integral_is_exact_and_has_zero_sampling_error() -> None:
    result = integrate(lambda _: 7.0, 2.0, 5.0, samples=20, seed=2026)
    assert result.estimate == 21.0
    assert result.standard_error == 0.0
    assert result.confidence_low == result.confidence_high == 21.0
    assert result.samples == 20
    assert result.seed == 2026
    assert result.lower == 2.0
    assert result.upper == 5.0
    assert result.confidence_level == 0.95
    with pytest.raises(FrozenInstanceError):
        result.estimate = 0.0  # type: ignore[misc]


def test_negative_and_zero_constant_integrals() -> None:
    assert integrate(lambda _: -2.0, 3.0, 8.0, samples=2).estimate == -10.0
    zero = integrate(lambda _: 0.0, -1.0, 1.0, samples=2)
    assert zero.estimate == zero.standard_error == 0.0


def test_sample_variance_and_width_against_independent_arithmetic() -> None:
    # Controlled observed values isolate the estimator arithmetic from sampling.
    heights = iter([1.0, 2.0, 3.0, 4.0])
    result = integrate(lambda _: next(heights), 3.0, 5.0, samples=4, seed=3)
    assert result.estimate == pytest.approx(5.0)
    assert result.standard_error == pytest.approx(math.sqrt(5 / 3))
    radius = statistics.NormalDist().inv_cdf(0.975) * math.sqrt(5 / 3)
    assert result.confidence_low == pytest.approx(5.0 - radius)
    assert result.confidence_high == pytest.approx(5.0 + radius)


def test_every_sample_is_used_and_locations_are_inside_supplied_bounds() -> None:
    locations: list[float] = []

    def function(x: float) -> float:
        locations.append(x)
        return x * x

    result = integrate(function, -2.0, 3.0, samples=120, seed=42)
    assert len(locations) == 120
    assert all(-2.0 <= x <= 3.0 for x in locations)
    with localcontext() as context:
        context.prec = 70
        observed = [Decimal.from_float(x * x) for x in locations]
        mean = sum(observed) / len(observed)
        variance = sum((value - mean) ** 2 for value in observed) / (len(observed) - 1)
        expected = float(Decimal(5) * mean)
        expected_error = float(Decimal(5) * (variance / len(observed)).sqrt())
    assert result.estimate == pytest.approx(expected, rel=1e-13)
    assert result.standard_error == pytest.approx(expected_error, rel=1e-13)


def test_seed_reproduces_run_without_touching_global_random_state() -> None:
    random.seed(8274)
    before = random.getstate()
    first = integrate(math.sin, 0.0, math.pi, samples=300, seed=2026)
    second = integrate(math.sin, 0.0, math.pi, samples=300, seed=2026)
    assert first == second
    assert random.getstate() == before
    assert first != integrate(math.sin, 0.0, math.pi, samples=300, seed=2027)


def test_known_integrals_are_consistent_with_reported_sampling_scale() -> None:
    # Seeds are prescribed; the bound is broad, not a guaranteed coverage assertion.
    for function, lower, upper, truth in [
        (lambda x: x, -2.0, 4.0, 6.0),
        (lambda x: x * x, 0.0, 1.0, 1 / 3),
        (math.sin, 0.0, math.pi, 2.0),
    ]:
        result = integrate(function, lower, upper, samples=20_000, seed=2026)
        assert abs(result.estimate - truth) < 7 * result.standard_error


def test_scaling_avoids_variance_square_overflow() -> None:
    values = iter([1e300, -1e300, 1e300, -1e300])
    result = integrate(lambda _: next(values), 0.0, 1e-300, samples=4)
    assert result.estimate == pytest.approx(0.0, abs=1e-15)
    assert result.standard_error == pytest.approx(1 / math.sqrt(3))


def test_width_scale_product_does_not_overflow_if_final_result_is_finite() -> None:
    result = integrate(lambda _: 1e300, 0.0, 1e-300, samples=2)
    assert result.estimate == pytest.approx(1.0)


def test_integrand_exception_propagates_without_silencing_programming_errors() -> None:
    def broken(_: float) -> float:
        raise RuntimeError("intentional function failure")

    with pytest.raises(RuntimeError, match="intentional function failure"):
        integrate(broken, 0, 1)


@pytest.mark.parametrize("function", [None, 3, "square", True])
def test_function_must_be_callable(function: Any) -> None:
    with pytest.raises(ValueError, match="callable"):
        integrate(function, 0, 1)


@pytest.mark.parametrize("bad", [True, None, "1", math.nan, math.inf, -math.inf, 10**400])
@pytest.mark.parametrize("parameter", ["lower", "upper", "confidence"])
def test_real_parameters_reject_nonfinite_or_nonnumeric_values(parameter: str, bad: Any) -> None:
    kwargs: dict[str, Any] = {"lower": 0.0, "upper": 1.0, "confidence": 0.95}
    kwargs[parameter] = bad
    with pytest.raises(ValueError):
        integrate(lambda x: x, samples=2, **kwargs)


@pytest.mark.parametrize("lower,upper", [(1, 1), (2, 1), (-1e308, 1e308)])
def test_bounds_require_finite_positive_width(lower: float, upper: float) -> None:
    with pytest.raises(ValueError, match="bounds"):
        integrate(lambda x: x, lower, upper)


@pytest.mark.parametrize("samples", [0, 1, -1, 1_000_001, 2.5, True, None, "20"])
def test_sample_count_is_explicitly_bounded(samples: Any) -> None:
    with pytest.raises(ValueError):
        integrate(lambda x: x, 0, 1, samples=samples)


@pytest.mark.parametrize("seed", [-1, 1.5, True, None, "20"])
def test_seed_is_a_nonnegative_integer(seed: Any) -> None:
    with pytest.raises(ValueError):
        integrate(lambda x: x, 0, 1, samples=2, seed=seed)


@pytest.mark.parametrize("confidence", [0, 1, -0.1, 1.1, 5e-324, math.nextafter(1, 0)])
def test_confidence_requires_representable_normal_quantile(confidence: float) -> None:
    with pytest.raises(ValueError):
        integrate(lambda x: x, 0, 1, samples=2, confidence=confidence)


@pytest.mark.parametrize("value", [True, None, "1", math.nan, math.inf, -math.inf, 10**400])
def test_invalid_integrand_outputs_fail_with_sample_context(value: Any) -> None:
    with pytest.raises(ValueError, match="integrand result at sample 1"):
        integrate(lambda _: value, 0, 1, samples=2)


@pytest.mark.parametrize("value,width", [(1e308, 2.0), (5e-324, 0.1)])
def test_unrepresentable_estimate_fails_explicitly(value: float, width: float) -> None:
    with pytest.raises(ValueError):
        integrate(lambda _: value, 0, width, samples=2)


def test_unrepresentable_interval_radius_fails_explicitly() -> None:
    values = iter([-1e308, 1e308])
    with pytest.raises(ValueError):
        integrate(lambda _: next(values), 0, 1, samples=2)


def test_unrepresentable_interval_endpoint_fails_explicitly() -> None:
    values = iter([1.7e308, 0.0])
    with pytest.raises(ValueError, match="endpoints"):
        integrate(lambda _: next(values), 0, 1, samples=2)


@settings(max_examples=60, deadline=None)
@given(constant=st.integers(-10000, 10000), width=st.integers(1, 100), count=st.integers(2, 50))
def test_constant_function_property(constant: int, width: int, count: int) -> None:
    result = integrate(lambda _: constant, -3, width - 3, samples=count, seed=17)
    assert result.estimate == pytest.approx(constant * width)
    assert result.standard_error == 0


@settings(max_examples=60, deadline=None)
@given(multiplier=st.integers(-100, 100), shift=st.integers(-100, 100))
def test_affine_integrand_transform_preserves_sampling_relationships(
    multiplier: int, shift: int
) -> None:
    base = integrate(lambda x: x * x, 1, 3, samples=100, seed=17)
    transformed = integrate(lambda x: multiplier * x * x + shift, 1, 3, samples=100, seed=17)
    assert transformed.estimate == pytest.approx(multiplier * base.estimate + 2 * shift)
    assert transformed.standard_error == pytest.approx(abs(multiplier) * base.standard_error)


@settings(max_examples=40, deadline=None)
@given(seed=st.integers(0, 1_000_000), count=st.integers(2, 200))
def test_interval_is_centered_and_ordered(seed: int, count: int) -> None:
    result = integrate(math.sin, -1, 2, samples=count, seed=seed)
    assert result.confidence_low <= result.estimate <= result.confidence_high
    assert result.standard_error >= 0
    assert result.confidence_low + result.confidence_high == pytest.approx(2 * result.estimate)
