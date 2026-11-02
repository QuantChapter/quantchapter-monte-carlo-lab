"""Generate the committed convergence evidence and its standalone figure."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from quantchapter_monte_carlo import __version__, convergence_experiment


def main() -> None:
    points = convergence_experiment(lambda x: x * x, 0, 1, exact=1 / 3, seed=2026)
    output = Path(__file__).resolve().parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "package_version": __version__,
        "integrand": "x squared on [0,1]",
        "source": "synthetic pseudorandom experiment; no external data",
        "exact_integral": 1 / 3,
        "confidence_level": 0.95,
        "seed_start": 2026,
        "seed_assignment": "seed_start + size_index * replications + replication_index",
        "replications_per_size": 80,
        "selection": "all prescribed runs included; no seed or path selection",
        "results": [asdict(point) for point in points],
    }
    (output / "convergence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    counts = [point.samples for point in points]
    errors = [point.root_mean_squared_error for point in points]
    theory = [math.sqrt(4 / (45 * count)) for count in counts]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    figure, axes = plt.subplots(figsize=(9.0, 5.7), layout="constrained")
    axes.loglog(counts, errors, color="#1959a6", marker="o", linewidth=1.8, label="Empirical RMSE")
    axes.loglog(
        counts,
        theory,
        color="#3f4650",
        linestyle="--",
        marker="s",
        markerfacecolor="white",
        linewidth=1.5,
        label=r"Analytic standard error $\sqrt{4/(45n)}$",
    )
    axes.set_title(
        r"Monte Carlo integration of $x^2$ on $[0,1]$"
        + "\n80 seeded replications per sample count",
        loc="left",
        pad=17,
        fontsize=15,
        fontweight="bold",
    )
    axes.set_xlabel("Function evaluations per replication (n)", labelpad=10)
    axes.set_ylabel("Error in integral units (log scale)", labelpad=10)
    axes.set_xticks(counts)
    axes.xaxis.set_major_formatter(ScalarFormatter())
    axes.tick_params(axis="x", which="minor", bottom=False)
    axes.grid(axis="y", which="major", color="#dfe3e7", linewidth=0.8)
    axes.spines[["top", "right"]].set_visible(False)
    axes.legend(frameon=False, loc="upper right")
    figure.get_layout_engine().set(rect=(0, 0.07, 1, 0.93))
    figure.text(
        0.015,
        0.018,
        "Synthetic experiment. Exact integral = 1/3. Every prescribed run is included.",
        fontsize=9.5,
        color="#4d535b",
    )
    figure.savefig(output / "convergence.png", dpi=180, facecolor="white")
    plt.close(figure)
    print(json.dumps({"sample_sizes": counts, "replications": 80, "outputs": "examples/output"}))


if __name__ == "__main__":
    main()
