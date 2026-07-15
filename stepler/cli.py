"""Command‑line interface for the Stepler package manager.

Supported commands (initial implementation):
- install <path-to-.step>
- remove <name> <version>
- list
- search <query> [--repo <path>]

The CLI is intentionally simple and can be extended later.
"""

import argparse
import sys
from pathlib import Path
from . import package

def _cmd_install(args: argparse.Namespace) -> int:
    try:
        install_path = Path(args.file)
        target, name = package.install(install_path)
        print(f"Installed {name} to {target}")
        return 0
    except Exception as e:
        print(f"Error installing package: {e}", file=sys.stderr)
        return 1

def _cmd_remove(args: argparse.Namespace) -> int:
    try:
        package.remove(args.name, args.version)
        print(f"Removed {args.name} version {args.version}")
        return 0
    except Exception as e:
        print(f"Error removing package: {e}", file=sys.stderr)
        return 1

def _cmd_list(_args: argparse.Namespace) -> int:
    installed = package.list_installed()
    if not installed:
        print("No packages installed.")
    else:
        for name, version in installed:
            print(f"{name}\t{version}")
    return 0

def _cmd_search(args: argparse.Namespace) -> int:
    repo = args.repo or Path.cwd()
    try:
        matches = package.search(str(repo), args.query)
        if not matches:
            print("No matching packages found.")
        else:
            for p in matches:
                meta = package.read_metadata(p)
                print(f"{meta.get('name')}\t{meta.get('version')}\t{p}")
        return 0
    except Exception as e:
        print(f"Error searching repository: {e}", file=sys.stderr)
        return 1

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stepler", description="Stepler – a simple Python package manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = subparsers.add_parser("install", help="Install a .step package")
    p_install.add_argument("file", help="Path to the .step archive")
    p_install.set_defaults(func=_cmd_install)

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove an installed package")
    p_remove.add_argument("name", help="Package name")
    p_remove.add_argument("version", help="Package version")
    p_remove.set_defaults(func=_cmd_remove)

    # list
    p_list = subparsers.add_parser("list", help="List installed packages")
    p_list.set_defaults(func=_cmd_list)

    # search
    p_search = subparsers.add_parser("search", help="Search for packages in a repository")
    p_search.add_argument("query", help="Search term (matches package name)")
    p_search.add_argument("--repo", help="Path to local repository (default: current directory)")
    p_search.set_defaults(func=_cmd_search)

    return parser

def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
