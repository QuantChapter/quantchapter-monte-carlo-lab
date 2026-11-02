# Verification record for 0.1.0

Local checks performed on 2 November 2026. This record separates local evidence
from remote CI and from learner observation; none implies certification.

| Check | Observed result |
| --- | --- |
| Ruff lint and formatting | Passed for package, tests, tools, examples, and notebook |
| Strict mypy | Passed for all five package modules |
| Windows Python 3.11.0 | 110 tests passed; 99.16% branch-aware coverage |
| Windows Python 3.12.0 | 110 tests passed; 99.16% branch-aware coverage |
| Windows Python 3.14.0 | 110 tests passed; 99.16% branch-aware coverage |
| Notebook | 16 cells executed in a fresh Python 3.12 kernel; one rendered figure |
| Saved-output verification | Source digest and saved numerical/text outputs checked by a fresh execution |
| Static figures | Standalone convergence PNG and saved notebook PNG visually inspected; titles, units, legends, and marks readable |
| Dependency audit | `pip-audit --skip-editable` reported no known vulnerabilities in the locked development environment |
| Distribution build | Wheel and source distribution built from the locked backend |
| Metadata checks | Strict Twine 7 checks passed; core metadata 2.4; runtime dependencies optional only |
| Installed wheel | Installed with `--no-deps` into a new environment outside the checkout; API and CLI passed |
| Workflow syntax | Actionlint 1.7.12 passed CI, release and CodeQL workflows; official release archive SHA-256 verified before use |
| Action dependencies | Every external action uses a full 40-character commit pin; checkout credentials are not persisted |

The numerical suite includes independently computed Decimal and exact arithmetic
references, analytic integrals, 160 Hypothesis-generated invariant cases,
streaming-moment extreme-scale checks, RNG isolation, all-replication experiments,
and CLI failure/no-overwrite behavior. Tests of simulation outcomes use
prespecified seeds and broad analytic-scale checks, not selected favorable paths.

The shipped convergence experiment uses $x^2$ on $[0,1]$, exact target $1/3$,
sample counts 100, 400, 1,600, and 6,400, and 80 replications each starting at
seed 2026. Every prescribed run is retained. The JSON next to the figure records
the inputs, complete summaries, seed mapping, and synthetic provenance.

Linux, macOS, Python 3.13, and remote GitHub jobs are configured in CI but were
not executed in this local Windows check. Their status is established by the
actual GitHub workflow runs after publication. The integrator inspected a fresh
HTML notebook export in a browser: mathematical typesetting, code and numeric
outputs, interval interpretation, the convergence plot at reading size, image
alternative text, and the adjacent exact-value table. The presentation review
gap reported during authoring is closed. Figure and content checks remain
distinct from observing a learner use the tutorial.

The teaching material is authored and technically checked, not learner-piloted.
Approximate normal intervals have no guaranteed finite-sample coverage.
Pseudorandom streams and floating-point calculations approximate the ideal
sampling model. No security, correctness, or educational outcome is guaranteed.
