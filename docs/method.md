# From an average height to an integral

Suppose we want the area beneath $f(x)=x^2$ between zero and one. The function
is nonnegative on this interval, so its integral is an ordinary area. We know
from calculus that the answer is $1/3$, but we will use that answer as an
independent check rather than build it into the estimator.

You need basic Python functions, averages, square roots, and the idea of a
definite integral. An integral adds signed contributions across an interval.
Negative function values therefore contribute negative area. The method below
works for those functions too, provided they are integrable and bounded on the
supplied interval.

## Give each location the same chance

Imagine choosing a location uniformly between zero and one. Uniform means
that equal-length subintervals have equal probability. Evaluate the function
at that location, repeat independently, and average the observed heights.
For a width-one interval, the average height estimates the integral itself.

For an interval $[a,b]$ of width $w=b-a$, multiply the average height by the
width. If $X_i$ is the location of sample $i$, and $Y_i=f(X_i)$ is its height,
the estimator based on $n$ observations is

$$
\widehat I_n = (b-a)\overline Y,
\qquad
\overline Y = \frac{Y_1+\cdots+Y_n}{n}.
$$

The hat marks an estimate. The bar marks an average. Under the independent
uniform-sampling model, the expected height is the integral divided by the
width, so multiplying by the width gives an unbiased estimator. Unbiased means
the average across repeated experiments equals the target in that model. It
does not mean that any single experiment returns the exact answer. Floating
point and pseudorandom generation approximate this mathematical model.

Consider a constant function $f(x)=7$ on $[2,5]$. Every sampled height is seven,
so the average is seven. The width is three, and the estimate is $3\times7=21$.
The result does not depend on where samples land. This is a useful first check
because it detects a forgotten width factor without depending on chance.

```python
from quantchapter_monte_carlo import integrate

constant = integrate(lambda x: 7.0, 2.0, 5.0, samples=20, seed=2026)
assert constant.estimate == 21.0
assert constant.standard_error == 0.0
```

## Estimate the uncertainty from the same observations

For $x^2$, sampled heights differ. Another random stream will produce a
different average. We need to report that variability with the estimate.

The sample variance measures the spread of heights around their own average:

$$
s^2=\frac{(Y_1-\overline Y)^2+\cdots+(Y_n-\overline Y)^2}{n-1}.
$$

The $n-1$ divisor accounts for estimating the mean from these same observations.
At least two observations are needed. Taking the square root gives $s$, the
sample standard deviation of individual heights. The average of independent
observations varies less than an individual observation: its estimated standard
error is $s/\sqrt n$. Multiplying by the width puts uncertainty into the same
units as the integral:

$$
\widehat{\operatorname{SE}}(\widehat I_n)
= (b-a)\frac{s}{\sqrt n}.
$$

For a numerical check, suppose four observed heights are $1,2,3,4$ on a
width-two interval. Their mean is $2.5$. Their squared deviations sum to
$2.25+0.25+0.25+2.25=5$, so $s^2=5/3$. The integral estimate is $2(2.5)=5$,
and its standard error is $2\sqrt{(5/3)/4}=\sqrt{5/3}$.

A zero sample standard error means only that the sampled heights coincide.
A function that is zero almost everywhere but has a narrow nonzero region may
be missed by every sample. The observed interval then gives false reassurance.
No finite list of function evaluations proves boundedness, integrability, or
that important regions have been explored.

## Interpret an approximate interval

For a 95% normal interval, the package uses the normal quantile about 1.96:

$$
\widehat I_n \pm 1.96\widehat{\operatorname{SE}}(\widehat I_n).
$$

This uses a central-limit approximation for independent uniform samples with
finite variance. A bounded function has finite variance on a finite interval,
but that does not tell us how quickly a particular sampling distribution
becomes close to normal. Small samples and rare influential regions can make
the approximation poor. The interval is not an exact finite-sample confidence
procedure, and a realized 95% interval is allowed to miss the true value.

The confidence level describes a repeated-experiment procedure under its
assumptions. It is not a posterior probability that a fixed unknown integral
lies inside the interval after observing the data. The package does not
estimate numerical bias from floating-point arithmetic or biased sampling.

## Check convergence across replications

For $f(x)=x^2$ on $[0,1]$, the expected height is $1/3$ and the expected squared
height is $1/5$. The height variance is therefore
$1/5-(1/3)^2=4/45$. The theoretical standard error is
$\sqrt{4/(45n)}$. Multiplying the sample count by four halves this theoretical
error. It does not force the absolute error of one realized run to halve.

The supplied experiment prespecifies sample sizes of 100, 400, 1,600, and 6,400,
with 80 replications each. Every run gets a distinct consecutive seed; no run
is discarded for an inconvenient result. The root mean squared error compares
all estimates with the known $1/3$ integral. The empirical coverage counts how
many approximate intervals contain that reference. These are simulation
measurements with their own finite-replication noise, not a proof of coverage.

As a short transfer check, what should change if we integrate the constant
function $f(x)=-2$ from three to eight? The width is five, so the integral is
$5(-2)=-10$. Every sampled value still coincides, so the standard error is zero.
Negative estimates are legitimate; a negative standard error would be an error.

For a different check, doubling $f$ doubles the estimate and the standard error
when the same samples are used. Adding a constant shifts the estimate by that
constant times the width but leaves sampling dispersion unchanged. The tests
exercise these relationships along with independent numerical references.

The implementation maintains scaled online moments to avoid storing every
observation and reduce avoidable overflow. It rejects nonfinite sampled values
and unrepresentable final results. It still uses finite-precision arithmetic.
Read the [API limits](api.md) before applying it to extreme scales or expensive
callables. The examples are authored teaching material, not learner-piloted
instruction or an investment model.
