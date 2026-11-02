# JSON report, schema version 1

The CLI writes one UTF-8 JSON object with a final newline and sorted keys.
No timestamps, paths, credentials, or machine identities enter the report.
`schema_version` identifies the report structure independently of
`package_version`, the software version.

| Field | Meaning |
| --- | --- |
| `integrand` | `square` for x*x, or `sine` for sin(x) in radians |
| `lower`, `upper` | Finite integration limits |
| `samples` | Count of function evaluations, including every draw |
| `seed` | Nonnegative integer seed for this private random stream |
| `estimate` | Interval width times sampled mean height |
| `standard_error` | Width times sample standard deviation divided by sqrt(samples) |
| `confidence_level` | Requested nominal level |
| `confidence_low`, `confidence_high` | Normal/CLT approximate interval endpoints |
| `conventions` | Sampling, variance divisor, interpretation, and reproducibility limits |

Nonfinite JSON numbers are forbidden. Zero standard error is allowed; it is not
proof of exactness. All CLI computation is offline. There is no `eval`, plugin
loading, arbitrary-code option, or automatic network access.

Exit status is zero on success and two for invalid arguments, nonfinite output,
unrepresentable results, and file errors. Invalid input prints an explanation to
stderr and never reports success JSON. `--output` creates parent directories
and publishes an already flushed staged file atomically using a same-directory
hard link. Existing destinations, including symlinks, are refused; failure
preserves existing contents and removes the staged temporary file. Filesystems
without hard links fail clearly. This is an atomic-visibility contract, not a
guarantee of pathname durability after power loss.
