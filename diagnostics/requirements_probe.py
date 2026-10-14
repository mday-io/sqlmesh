"""Temporary pytest plugin for SQLMesh Windows dependency-inference diagnosis.

Load with `-p requirements_probe` and pass `--requirements-probe-json PATH`.
It wraps the existing _build_requirements function without changing SQLMesh code.
"""
from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

_PREFIX = "[REQDIAG-20261013]"


def pytest_addoption(parser):
    group = parser.getgroup("requirements diagnosis")
    group.addoption(
        "--requirements-probe-json",
        action="store",
        default=None,
        help="Append requirement-inference diagnostics as JSONL to this path.",
    )


def _version(metadata, package):
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None


def _import_root(payload):
    start = "from " if payload.startswith("from ") else "import "
    return payload.split(start)[1].split()[0].split(".")[0]


def _runtime(metadata, package_map):
    try:
        pendulum_dist = metadata.distribution("pendulum")
        pendulum_top_level = pendulum_dist.read_text("top_level.txt")
        pendulum_files = getattr(pendulum_dist, "files", None) or ()
        pendulum_package_files = [
            str(item) for item in pendulum_files if str(item).lower().startswith("pendulum/")
        ][:12]
        pendulum_metadata_error = None
    except metadata.PackageNotFoundError as error:
        pendulum_top_level = None
        pendulum_package_files = []
        pendulum_metadata_error = str(error)

    packages = (
        "pendulum",
        "dlt",
        "sqlmesh",
        "pytest",
        "importlib-metadata",
        "pandas",
        "numpy",
        "ipywidgets",
    )
    return {
        "python": sys.version,
        "platform": sys.platform,
        "os_name": os.name,
        "platform_description": platform.platform(),
        "executable": sys.executable,
        "metadata_module": getattr(metadata, "__file__", None),
        "package_versions": {name: _version(metadata, name) for name in packages},
        "pendulum_top_level_txt": pendulum_top_level,
        "pendulum_package_files_sample": pendulum_package_files,
        "pendulum_metadata_error": pendulum_metadata_error,
        "packages_distributions_pendulum_key": sorted(package_map.get("pendulum", []) or []),
        "modules_mapped_to_pendulum": sorted(
            module
            for module, distributions in package_map.items()
            if "pendulum" in (distributions or [])
        ),
    }


def _emit(config, record):
    rendered = json.dumps(record, sort_keys=True, ensure_ascii=True)
    print(f"{_PREFIX} {rendered}", flush=True)
    destination = config.getoption("--requirements-probe-json")
    if destination:
        output_path = Path(destination)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(rendered + "\n")


def pytest_configure(config):
    from sqlmesh.core import context_diff

    original = context_diff._build_requirements
    if getattr(original, "_requirements_probe_wrapped", False):
        return

    call_number = 0

    def traced_build_requirements(
        provided_requirements,
        excluded_requirements,
        snapshots,
        infer_python_dependencies=True,
    ):
        nonlocal call_number
        call_number += 1
        snapshots = tuple(snapshots)
        metadata = context_diff.metadata
        package_map = metadata.packages_distributions()
        imports = {}

        for snapshot in snapshots:
            if not snapshot.is_model:
                continue
            snapshot_name = str(snapshot.name)
            for alias, executable in snapshot.model.python_env.items():
                if executable.kind != "import":
                    continue
                payload = executable.payload
                try:
                    module = _import_root(payload)
                except (IndexError, AttributeError):
                    module = "<parse-error>"
                distributions = sorted(package_map.get(module, []) or [])
                key = (snapshot_name, str(alias), str(payload), module)
                imports[key] = {
                    "snapshot": snapshot_name,
                    "alias": str(alias),
                    "payload": str(payload),
                    "root_module": module,
                    "mapped_distributions": distributions,
                }

        try:
            inferred = original(
                provided_requirements,
                excluded_requirements,
                snapshots,
                infer_python_dependencies=infer_python_dependencies,
            )
        except BaseException as error:
            record = {
                "call": call_number,
                "runtime": _runtime(metadata, package_map),
                "provided_requirement_names": sorted(provided_requirements),
                "excluded_requirement_names": sorted(excluded_requirements),
                "infer_python_dependencies": infer_python_dependencies,
                "snapshot_count": len(snapshots),
                "serialized_imports": [imports[key] for key in sorted(imports)],
                "pendulum_related_imports": [
                    item
                    for item in imports.values()
                    if item["root_module"] == "pendulum"
                    or "pendulum" in item["mapped_distributions"]
                ],
                "inference_error": f"{type(error).__name__}: {error}",
            }
            _emit(config, record)
            raise

        _emit(
            config,
            {
                "call": call_number,
                "runtime": _runtime(metadata, package_map),
                "provided_requirement_names": sorted(provided_requirements),
                "excluded_requirement_names": sorted(excluded_requirements),
                "infer_python_dependencies": infer_python_dependencies,
                "snapshot_count": len(snapshots),
                "serialized_imports": [imports[key] for key in sorted(imports)],
                "pendulum_related_imports": [
                    item
                    for item in imports.values()
                    if item["root_module"] == "pendulum"
                    or "pendulum" in item["mapped_distributions"]
                ],
                "inferred_requirement_names": sorted(inferred),
                "inferred_requirement_versions": inferred,
            },
        )
        return inferred

    traced_build_requirements._requirements_probe_wrapped = True
    context_diff._build_requirements = traced_build_requirements
