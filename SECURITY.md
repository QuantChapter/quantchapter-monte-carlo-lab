# Security policy

The current 0.1.x release line is the supported line. There is no promised
response time or security certification. Report suspected vulnerabilities
privately through GitHub's private vulnerability reporting when enabled, or
email [support@quantchapter.com](mailto:support@quantchapter.com). Include the
affected version, reproduction steps, expected impact, and a minimal example.
Do not place credentials or sensitive data in public issues.

The CLI is offline and exposes only predefined scalar functions. The Python API
executes the callable supplied by its caller; this is not a sandbox for
untrusted code. Evaluation-count limits do not stop a callable that itself
hangs or performs destructive actions. Use only trusted callables.

Reports refuse overwriting existing destinations. Hard-link publication gives
atomic visibility; it does not guarantee directory durability after power loss.
Use normal filesystem permissions to control access. The random generator is
for numerical examples, never for keys, tokens, or security decisions.

Development dependencies and GitHub Actions require ongoing updates. A clean
dependency audit means no advisories were reported by that particular audit;
it is not proof that the code or dependencies contain no vulnerabilities.
