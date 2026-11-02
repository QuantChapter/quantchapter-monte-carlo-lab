# Contributing

Contributions should improve a specific numerical, teaching, or reproducibility
need. Open an issue describing the behavior and an independently checkable case
before proposing a broad new method. Do not add dependencies to the core merely
to shorten a small calculation.

```bash
uv sync --locked --all-extras --dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy
uv run --frozen pytest
uv run --frozen python tools/verify_notebooks.py
uv run --frozen pip-audit --skip-editable
uv build --no-build-isolation
uv run --frozen python -m twine check --strict dist/*
uv run --frozen python tools/smoke_wheel.py
```

The locked environment includes test, quality, and notebook tools. Supported
Python versions are 3.11–3.14. The core requires no runtime dependencies.
Keep reference calculations independent, include a meaningful failure case,
and distinguish mathematical model assumptions from floating-point behavior.
Do not weaken numerical checks to make an implementation pass.

Use the notebook's recorded seed and all experiment replications. Keep saved
outputs useful when opened without a kernel. A modified notebook must execute
top to bottom and its plots must be visually inspected. Avoid absolute local
paths and machine-specific output. Document API or report-schema changes.
After a deliberate teaching/source update, run
`uv run --frozen python tools/verify_notebooks.py --write` to refresh the saved
execution and its source digest. The default verifier executes read-only and
compares the saved numerical/text outputs rather than silently updating them.

Changes enter through a pull request with purpose, resulting behavior, and
actual verification. Report security issues privately as described in
[SECURITY.md](SECURITY.md). No financial results, learner outcomes, certification,
or deployment status may be invented. By contributing, you agree that your
contribution may be distributed under this repository's MIT license.
