# Copyright 2025 Marimo. All rights reserved.
from __future__ import annotations

import functools
import os
import pathlib
import site
from typing import Any


@functools.cache
def _getsitepackages() -> list[pathlib.Path]:
    try:
        # Try to get global site-packages (not available in virtual envs)
        site_packages_dirs = [
            pathlib.Path(p).resolve() for p in site.getsitepackages()
        ]
    except AttributeError:
        # Fallback for virtual environments or restricted environments
        try:
            site_packages_dirs = [
                pathlib.Path(site.getusersitepackages()).resolve()
            ]
        except AttributeError:
            # Fallback to empty, and handle other ways.
            return []
    return site_packages_dirs


def is_local_module(spec: Any) -> bool:
    """Check if a module is local (not under site-packages).

    Uses Python's site module to get actual site-packages directories,
    making it more robust across different Python installations and OS.
    """
    if spec is None or spec.origin is None:
        return True  # Assume local if we can't determine

    if "site-packages" in spec.origin:
        return False

    # Skip pathlib.Path.resolve() if possible by pre-resolving user/site-packages dirs in _getsitepackages
    # and comparing as strings for much faster comparisons.
    origin = spec.origin
    try:
        # resolve only if needed and cache result
        module_path_resolved = None
        site_packages_dirs = _getsitepackages()
        if not site_packages_dirs:
            # Ultimate fallback: use string matching
            return "site-packages" not in pathlib.Path(origin).parts

        # Check using fast string-based prefix matching of canonical absolute paths
        module_path_abs = pathlib.Path(origin)
        # Only call .resolve() once if we need to (and only if not absolute)
        if not module_path_abs.is_absolute():
            module_path_abs = module_path_abs.resolve()
        # Convert to string once
        module_path_str = str(module_path_abs)

        for site_dir in site_packages_dirs:
            site_dir_str = str(site_dir)
            # Fast check: site_dir + separator is prefix of module_path_str
            if module_path_str.startswith(site_dir_str) and (
                module_path_str == site_dir_str
                or module_path_str[len(site_dir_str)] in {"/", "\\"}
            ):
                return False  # Module is in site-packages
    except (OSError, ValueError):
        # Handle path resolution issues
        pass

    return True  # Module is local


def module_exists_in_site_packages(module_name: str) -> bool:
    """Check if a module exists in site-packages."""
    try:
        # Get all site-packages directories
        site_packages_dirs = site.getsitepackages()
        if hasattr(site, "getusersitepackages"):
            site_packages_dirs.append(site.getusersitepackages())

        for site_dir in site_packages_dirs:
            if not os.path.exists(site_dir):
                continue

            # Check for package directory
            package_dir = os.path.join(site_dir, module_name)
            if os.path.isdir(package_dir):
                return True

            # Check for .py file
            py_file = os.path.join(site_dir, f"{module_name}.py")
            if os.path.isfile(py_file):
                return True

            # Check for .pth files or other package indicators
            for entry in os.listdir(site_dir):
                module = entry.split("-", 1)[0]
                if module == module_name and (
                    entry.endswith(".egg-info")
                    or entry.endswith(".dist-info")
                    or entry.endswith(".egg")
                ):
                    return True

    except Exception:
        # If we can't check site-packages, assume it might exist
        return False

    return False


def has_local_conflict(module_name: str, directory: str) -> bool:
    """Check if there's a local file or package that conflicts with the module name."""
    # Needs to have external module in site-packages to be a conflict
    if not module_exists_in_site_packages(module_name):
        return False

    # Check for local .py file with same name
    local_py = os.path.join(directory, f"{module_name}.py")
    if os.path.isfile(local_py):
        return True

    # Check for local package directory
    local_pkg = os.path.join(directory, module_name)
    if os.path.isdir(local_pkg) and os.path.isfile(
        os.path.join(local_pkg, "__init__.py")
    ):
        return True

    return False
