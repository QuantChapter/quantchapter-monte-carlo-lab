# Public API

```python
integrate(function, lower, upper, *, samples=10000, seed=0, confidence=0.95)
convergence_experiment(function, lower, upper, *, exact,
    sample_sizes=(100, 400, 1600, 6400), replications=80, seed=0, confidence=0.95)
```

`integrate` returns a frozen `IntegrationResult` with `estimate`,
`standard_error`, `confidence_level`, `confidence_low`, `confidence_high`,
`samples`, `seed`, `lower`, and `upper`. Quantities use integral units.

The function must map one real scalar to one finite real scalar. It should be
deterministic and bounded/integrable over the supplied interval; those global
properties cannot be verified by sampling. Numeric inputs accept real scalar
values that convert to finite floats; booleans and numeric strings are rejected.
The seed must be a nonnegative integer. Samples must be an integer from 2 through
1,000,000. Bounds must increase strictly with finite positive representable
width. Confidence must be strictly between zero and one, with a representable
positive finite normal quantile. Extremely endpoint-adjacent levels fail.

`ValueError` reports invalid parameters, sampled outputs, or unrepresentable
results. Exceptions raised by your function propagate unchanged; the package
does not suppress programming errors. A callable runs with your process's
privileges and should never be an untrusted program. Sampling does not modify
Python's global random state. Floating-point sampling may land on a rounded
endpoint, and cannot represent a mathematical continuous uniform distribution
exactly. A fixed seed repeats a run in a fixed Python environment; cross-version
bit identity is not a compatibility contract.

`convergence_experiment` returns a tuple of frozen `ConvergencePoint` records:
`samples`, `replications`, `root_mean_squared_error`, `mean_standard_error`, and
`empirical_coverage`. Supply the independent analytic target via `exact`.
Sample sizes must be nonempty, unique, increasing integers. Replications range
from 2 through 1,000, and total work cannot exceed 10,000,000 evaluations. Seeds
are `seed + size_index * replications + replication_index`. No result is
discarded or retried because of its error. Distinct seeded pseudorandom streams
approximate independent trials; they do not establish mathematical independence.

The runtime does not provide cancellation or timeouts for arbitrary expensive
callables. Sample limits bound evaluation counts, not wall-clock duration.
Changing the algorithm or random-stream contract requires a documented release.
