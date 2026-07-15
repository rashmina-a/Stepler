"""Utilities for handling .step package archives.

The .step format is a simple tar.gz archive containing:
- a `metadata.json` file with package name, version, and optional dependencies
- the package files under a top‑level directory named after the package

This module provides functions to create, extract, and inspect .step files.
"""

import json
import os
import sys
import tarfile
from pathlib import Path
from typing import Dict, List, Tuple

# Directory where installed packages are stored
INSTALL_ROOT = Path.home() / ".stepler" / "packages"

# Directory for globally accessible command‑line wrappers
GLOBAL_BIN = Path.home() / ".local" / "bin"

def ensure_install_root() -> None:
    """Create the installation root directory if it does not exist."""
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)

def read_metadata(step_path: Path) -> Dict:
    """Read the ``metadata.json`` file from a .step archive.

    The original implementation expected the file to be stored at the exact
    path ``metadata.json``. In practice many tar archives store members with a
    leading ``./`` (e.g. ``./metadata.json``) or place the file inside a top‑
    level directory. To make the installer more tolerant we search through all
    members and pick the first one whose name ends with ``metadata.json``.

    Args:
        step_path: Path to the .step archive.
    Returns:
        Dictionary with metadata (name, version, dependencies).
    """
    with tarfile.open(step_path, "r:gz") as tar:
        # Find a member whose name ends with 'metadata.json'
        metadata_member = None
        for m in tar.getmembers():
            # Normalise the name by stripping any leading './'
            name = m.name.lstrip("./")
            if name.endswith("metadata.json"):
                metadata_member = m
                break
        if metadata_member is None:
            raise ValueError("Invalid .step archive: missing metadata.json")
        f = tar.extractfile(metadata_member)
        if f is None:
            raise ValueError("Unable to read metadata.json from archive")
        return json.load(f)

def install(step_path: str) -> Tuple[str, str]:
    """Install a .step package.

    The package is extracted to ``$HOME/.stepler/packages/<name>-<version>``.
    Returns the installed path and the package name.
    """
    step_path = Path(step_path)
    if not step_path.is_file():
        raise FileNotFoundError(f"Package file not found: {step_path}")

    meta = read_metadata(step_path)
    name = meta.get("name")
    version = meta.get("version")
    if not name or not version:
        raise ValueError("metadata.json must contain 'name' and 'version'")

    target_dir = INSTALL_ROOT / f"{name}-{version}"
    if target_dir.exists():
        raise FileExistsError(f"Package {name} version {version} is already installed")

    ensure_install_root()
    with tarfile.open(step_path, "r:gz") as tar:
        # Extract all members preserving the top‑level directory structure
        tar.extractall(path=target_dir)

    # After extraction, optionally create a global executable wrapper.
    # The metadata may contain an "entrypoint" field that points to a Python
    # script relative to the package root (e.g., "main.py"). If present we
    # generate a small wrapper script in ``~/.local/bin`` that runs the
    # entrypoint with the system Python interpreter.
    entrypoint = meta.get("entrypoint")
    if entrypoint:
        try:
            GLOBAL_BIN.mkdir(parents=True, exist_ok=True)
            wrapper_path = GLOBAL_BIN / name
            script_path = target_dir / entrypoint
            # Create a tiny executable that forwards to the entrypoint.
            # The metadata may specify an ``interpreter`` (e.g., "python3",
            # "node", "bash"). If omitted we fall back to ``python3`` for
            # backward compatibility.
            interpreter = meta.get("interpreter", "python3")
            # For Python we keep the previous behaviour (run the script as a
            # module). For other languages we simply exec the interpreter with
            # the script path and forward any additional arguments.
            if interpreter.startswith("python"):
                # NOTE: The original string accidentally added a stray '.'
                # after ``Path('{script_path}')`` which caused a syntax error.
                # The line below correctly creates a ``Path`` object and
                # resolves it.
                wrapper_content = (
                    f"#!/usr/bin/env {interpreter}\n"
                    f"import runpy, sys, pathlib\n"
                    f"pkg_path = pathlib.Path('{script_path}').resolve()\n"
                    f"sys.argv[0] = str(pkg_path)\n"
                    f"runpy.run_path(str(pkg_path), run_name='__main__')\n"
                )
            else:
                # Generic wrapper: exec the interpreter with the script path.
                # "$@" forwards any arguments supplied to the wrapper.
                wrapper_content = (
                    f"#!/usr/bin/env {interpreter}\n"
                    f"exec {interpreter} '{script_path}' \"$@\"\n"
                )
            wrapper_path.write_text(wrapper_content, encoding="utf-8")
            wrapper_path.chmod(wrapper_path.stat().st_mode | 0o111)  # make executable
        except Exception as e:
            # Non‑fatal: warn the user but do not abort installation.
            print(f"Warning: could not create global wrapper for {name}: {e}", file=sys.stderr)
    return str(target_dir), name

def list_installed() -> List[Tuple[str, str]]:
    """Return a list of installed packages as (name, version) tuples."""
    ensure_install_root()
    packages = []
    for entry in INSTALL_ROOT.iterdir():
        if entry.is_dir():
            # Expect directory name format name-version
            parts = entry.name.rsplit("-", 1)
            if len(parts) == 2:
                packages.append((parts[0], parts[1]))
    return packages

def remove(name: str, version: str) -> None:
    """Remove an installed package."""
    target_dir = INSTALL_ROOT / f"{name}-{version}"
    if not target_dir.exists():
        raise FileNotFoundError(f"Package {name} version {version} is not installed")
    # Recursively delete the directory
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
    os.rmdir(target_dir)

def search(repo_path: str, query: str) -> List[Path]:
    """Search a local repository directory for .step files matching the query.

    Args:
        repo_path: Path to a directory containing .step files.
        query: Simple substring to match against the package name.
    Returns:
        List of matching Path objects.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise NotADirectoryError(f"Repository path not found: {repo_path}")
    matches = []
    for step_file in repo.rglob("*.step"):
        try:
            meta = read_metadata(step_file)
            if query.lower() in meta.get("name", "").lower():
                matches.append(step_file)
        except Exception:
            # Skip invalid archives
            continue
    return matches
