"""The complete offline CLI and transactional no-overwrite output contract."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from quantchapter_monte_carlo import __version__, integrate
from quantchapter_monte_carlo.cli import main


def test_stdout_json_agrees_with_independent_public_api(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["square", "--seed", "2026", "--samples", "1000"]) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    expected = integrate(lambda x: x * x, 0, 1, samples=1000, seed=2026)
    assert report["estimate"] == expected.estimate
    assert report["standard_error"] == expected.standard_error
    assert report["schema_version"] == 1
    assert report["package_version"] == __version__
    assert report["conventions"]["variance_divisor"] == "samples - 1"
    assert captured.err == ""


def test_sine_cli_uses_radians(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sine", "--upper", str(math.pi), "--samples", "1000", "--seed", "2026"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["integrand"] == "sine"
    assert abs(report["estimate"] - 2) < 7 * report["standard_error"]


def test_output_creates_parents_and_preserves_existing_contents(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "nested" / "result.json"
    args = ["square", "--samples", "20", "--output", str(output)]
    assert main(args) == 0
    original = output.read_bytes()
    assert json.loads(original)["samples"] == 20
    assert original.endswith(b"\n")
    assert main(args) == 2
    assert output.read_bytes() == original
    assert sorted(path.name for path in output.parent.iterdir()) == ["result.json"]
    assert capsys.readouterr().err


def test_output_failures_leave_no_staged_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail_link(*args: object, **kwargs: object) -> None:
        raise OSError("simulated filesystem has no hard links")

    monkeypatch.setattr("quantchapter_monte_carlo.cli.os.link", fail_link)
    assert main(["square", "--samples", "2", "--output", str(tmp_path / "result.json")]) == 2
    assert list(tmp_path.iterdir()) == []
    assert "hard links" in capsys.readouterr().err


def test_symlink_destination_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(Path, "is_symlink", lambda _: True)
    assert main(["square", "--samples", "2", "--output", str(tmp_path / "link.json")]) == 2
    assert "symbolic link" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [
        ["square", "--samples", "1"],
        ["square", "--seed", "-1"],
        ["square", "--lower", "nan"],
        ["square", "--upper", "inf"],
        ["square", "--lower", "2", "--upper", "1"],
        ["square", "--confidence", "1"],
        ["square", "--lower", "1e200", "--upper", "2e200"],
    ],
)
def test_bad_inputs_produce_error_without_success_json(
    arguments: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(arguments) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("quantchapter-monte-carlo:")


def test_unknown_integrand_is_never_evaluated(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["__import__('os').getcwd()"])
    assert error.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_version_is_available_without_simulation(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--version"])
    assert error.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_module_entrypoint_runs_end_to_end() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantchapter_monte_carlo",
            "square",
            "--samples",
            "100",
            "--seed",
            "2026",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["samples"] == 100
    assert result.stderr == ""
