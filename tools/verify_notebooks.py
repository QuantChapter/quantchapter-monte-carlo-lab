"""Execute the tutorial and compare saved output; --write explicitly refreshes it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]


def source_digest(notebook: nbformat.NotebookNode) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps([cell.source for cell in notebook.cells]).encode("utf-8"))
    for path in sorted((ROOT / "src/quantchapter_monte_carlo").glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8"))
    return digest.hexdigest()


def text_outputs(notebook: nbformat.NotebookNode) -> list[list[str]]:
    return [
        [
            output.get("text", output.get("data", {}).get("text/plain", ""))
            for output in cell.get("outputs", [])
        ]
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh the saved executed notebook")
    args = parser.parse_args()
    path = ROOT / "notebooks/01-integration-and-uncertainty.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    original_text = text_outputs(notebook)
    digest = source_digest(notebook)
    if not args.write and notebook.metadata.get("quantchapter_source_sha256") != digest:
        raise ValueError(
            "Saved tutorial output is stale; rerun with --write after reviewing changes"
        )
    for cell in notebook.cells:
        cell.metadata.pop("execution", None)
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        record_timing=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.km = client.create_kernel_manager()
    client.km.kernel_spec.argv = [
        sys.executable,
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ]
    client.execute()
    figures = 0
    for cell in notebook.cells:
        cell.metadata.pop("execution", None)
        if cell.cell_type == "code" and cell.execution_count is None:
            raise ValueError("Notebook contains an unexecuted code cell")
        for output in cell.get("outputs", []):
            if output.output_type == "error":
                raise ValueError("Notebook contains an execution error")
            if output.output_type in {
                "display_data",
                "execute_result",
            } and "image/png" in output.get("data", {}):
                figures += 1
                output.metadata["image/png"] = {
                    "alt": "Empirical RMSE and analytic standard error for x squared on [0,1]; "
                    "80 seeded replications at each of 100,400,1600,6400 samples. "
                    "The complete numerical table is immediately above the figure."
                }
            serialized = json.dumps(output, ensure_ascii=False)
            for prefix in ("C:\\\\Users\\\\", "C:/Users/", "/Users/", "/home/"):
                if prefix in serialized:
                    raise ValueError("Machine-local path in notebook output")
    if figures != 1:
        raise ValueError(f"Expected one rendered explanatory figure, found {figures}")
    notebook.metadata["language_info"] = {"name": "python"}
    notebook.metadata["quantchapter_source_sha256"] = digest
    nbformat.validate(notebook)
    if args.write:
        nbformat.write(notebook, path)
    elif text_outputs(notebook) != original_text:
        raise ValueError("Saved numerical/text outputs differ; review and rerun with --write")
    preview = ROOT / ".notebook-preview"
    preview.mkdir(exist_ok=True)
    html, _ = HTMLExporter(template_name="lab").from_notebook_node(notebook)
    (preview / "tutorial.html").write_text(html, encoding="utf-8")
    print(
        f"Executed {len(notebook.cells)} cells; verified {figures} figure "
        "and source/output binding."
    )


if __name__ == "__main__":
    main()
