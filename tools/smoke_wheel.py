"""Install one wheel into an isolated environment and execute it outside the checkout."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import venv
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    wheels = list((root / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("Expected exactly one built wheel in dist")
    with tempfile.TemporaryDirectory(prefix="quantchapter-wheel-") as temporary:
        directory = Path(temporary)
        environment = directory / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        cli = scripts / (
            "quantchapter-monte-carlo.exe" if os.name == "nt" else "quantchapter-monte-carlo"
        )
        subprocess.run(
            [str(python), "-I", "-m", "pip", "install", "--no-deps", str(wheels[0])],
            cwd=directory,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "from quantchapter_monte_carlo import integrate; "
                "r=integrate(lambda x:7.,2.,5.,samples=20); "
                "assert r.estimate ==21. and r.standard_error==0.",
            ],
            cwd=directory,
            check=True,
        )
        destination = directory / "report.json"
        subprocess.run(
            [
                str(cli),
                "square",
                "--samples",
                "1000",
                "--seed",
                "2026",
                "--output",
                str(destination),
            ],
            cwd=directory,
            check=True,
        )
        report = json.loads(destination.read_text(encoding="utf-8"))
        assert report["schema_version"] == 1 and report["samples"] == 1000
        assert report["standard_error"] > 0
        print(
            "Installed-wheel API and CLI passed outside the checkout with no runtime dependencies."
        )


if __name__ == "__main__":
    main()
