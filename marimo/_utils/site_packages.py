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
        site_packages_dirs = [pathlib.Path(p) for p in site.getsitepackages()]
    except AttributeError:
        # Fallback for virtual environments or restricted environments
        try:
            site_packages_dirs = [pathlib.Path(site.getusersitepackages())]
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

    module_path = pathlib.Path(spec.origin).resolve()
    site_packages_dirs = _getsitepackages()
    if not site_packages_dirs:
        # Ultimate fallback: use string matching
        return "site-packages" not in module_path.parts

    # Check if module is in any site-packages directory
    for site_dir in site_packages_dirs:
        try:
            if module_path.is_relative_to(site_dir):
                return False  # Module is in site-packages
        except (OSError, ValueError):
            # Handle path resolution issues
            continue

    return True  # Module is local


def module_exists_in_site_packages(module_name: str) -> bool:
    """Check if a module exists in site-packages."""
    try:
        # Get all site-packages directories
        site_packages_dirs = site.getsitepackages()
        if hasattr(site, "getusersitepackages"):
            user_site = site.getusersitepackages()
            if user_site not in site_packages_dirs:
                site_packages_dirs.append(user_site)

        # Precompute targets for faster endswith
        suffixes = (".egg-info", ".dist-info", ".egg")
        # Allocate function locals
        join = os.path.join
        isdir = os.path.isdir
        isfile = os.path.isfile
        exists = os.path.exists
        listdir = os.listdir

        for site_dir in site_packages_dirs:
            if not exists(site_dir):
                continue

            # Check for package directory
            package_dir = join(site_dir, module_name)
            if isdir(package_dir):
                return True

            # Check for .py file
            py_file = join(site_dir, f"{module_name}.py")
            if isfile(py_file):
                return True

            # Check for .pth files or other package indicators
            try:
                entries = listdir(site_dir)
            except OSError:
                # Directory may not be accessible
                continue

            # membership/endswith chain optimized
            for entry in entries:
                # Performance: avoid split if not needed
                if not entry.endswith(suffixes):
                    continue
                module = entry.split("-", 1)[0]
                if module == module_name:
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
