"""A small offline CLI with predefined functions and versioned JSON output."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .core import integrate


def _write_output(destination: Path, content: str) -> None:
    """Publish a staged file atomically, refusing replacement even during races."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ValueError("output must not be a symbolic link")
    staged: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent, delete=False
        ) as stream:
            staged = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staged, destination)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Return zero on success and two for invalid input or output failures."""
    parser = argparse.ArgumentParser(
        prog="quantchapter-monte-carlo", description="Offline uniform Monte Carlo integration."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "integrand", choices=("square", "sine"), help="x*x or sin(x); no evaluated code"
    )
    parser.add_argument("--lower", type=float, default=0.0)
    parser.add_argument("--upper", type=float, default=1.0)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--output", type=Path, help="write JSON without overwrite; default: stdout")
    args = parser.parse_args(argv)
    function = (lambda x: x * x) if args.integrand == "square" else math.sin
    try:
        result = integrate(
            function,
            args.lower,
            args.upper,
            samples=args.samples,
            seed=args.seed,
            confidence=args.confidence,
        )
        report = {
            "schema_version": 1,
            "package_version": __version__,
            "integrand": args.integrand,
            **asdict(result),
            "conventions": {
                "sampling": "uniform pseudorandom; private Python Random(seed) stream",
                "variance_divisor": "samples - 1",
                "interval": "approximate normal/CLT; not a finite-sample coverage guarantee",
                "reproducibility": (
                    "fixed Python environment; cross-version bit identity not promised"
                ),
                "purpose": "educational numerical integration",
            },
        }
        content = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output is None:
            sys.stdout.write(content)
        else:
            _write_output(args.output, content)
    except (OSError, ValueError, OverflowError) as exc:
        print(f"quantchapter-monte-carlo: {exc}", file=sys.stderr)
        return 2
    return 0
