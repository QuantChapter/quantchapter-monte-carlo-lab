# QuantChapter Monte Carlo Lab

An independent educational Python package for uniform Monte Carlo integration.
Keep the numerical runtime dependency-free and the public scope small.

- Support Python 3.11–3.14. Use typed interfaces and explicit validation.
- Explain estimator, standard error, interval assumptions, and floating-point
  limits honestly. No simulation output establishes future financial performance.
- Use local random generators, fixed documented seeds, and all prescribed
  replications. Never select a seed for a visually favorable result.
- Tests must independently reconstruct mathematics, not mirror implementation.
- Run Ruff, strict mypy, branch-covered tests, notebook execution, dependency
  audit, packaging checks, and an isolated installed-wheel smoke test.
- Keep Python environments, caches, credentials, personal names, and local paths
  out of commits. Check the intended Git diff before committing.
- Pin every GitHub Action to a verified commit, disable persisted credentials,
  and grant jobs only their needed permissions.
- Do not add trading, financial advice, network execution, or evaluated user code.
- Never poll a running job or agent more frequently than once every five minutes.
  Prefer completion events and blocking waits; continue independent useful work.
