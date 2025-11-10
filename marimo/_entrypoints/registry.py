# Copyright 2025 Marimo. All rights reserved.
import os
from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Generic, Optional, TypeVar, cast

from marimo import _loggers
from marimo._entrypoints.ids import KnownEntryPoint

if TYPE_CHECKING:
    from importlib.metadata import EntryPoints

T = TypeVar("T")
LOGGER = _loggers.marimo_logger()


class EntryPointRegistry(Generic[T]):
    """A registry for entry points.

    This registry allows entry points to be loaded in two ways:
    1. Through an explicit call to `.register(name, value)`
    2. By looking for Python packages that provide a setuptools entry point group

    The registry can be configured with allowlists and denylists through environment variables:
    - MARIMO_{GROUP}_ALLOWLIST: Comma-separated list of allowed extensions
    - MARIMO_{GROUP}_DENYLIST: Comma-separated list of denied extensions

    Example:
        MARIMO_CELL_EXECUTOR_ALLOWLIST=my-executor,another-executor
        MARIMO_CELL_EXECUTOR_DENYLIST=denied-executor

    Usage:
        registry = EntryPointRegistry[MyType]("my_entrypoint_group")
    """

    def __init__(self, entry_point_group: KnownEntryPoint) -> None:
        """Create an EntryPointRegistry for a named entry point group.

        Args:
            entry_point_group: The name of the entry point group.
        """
        self.entry_point_group: KnownEntryPoint = entry_point_group
        self._plugins: dict[str, T] = {}

        # Convert entry point group to env var format (e.g. marimo.cell.executor -> MARIMO_CELL_EXECUTOR)
        self._env_prefix = entry_point_group.replace(".", "_").upper()
        self._denylist_var = f"{self._env_prefix}_DENYLIST"
        self._allowlist_var = f"{self._env_prefix}_ALLOWLIST"
        self._denylist: set[str] | None = None
        self._allowlist: set[str] | None = None

    def _is_allowed(self, name: str) -> bool:
        """Check if an extension name is allowed based on environment variables.

        Args:
            name: The name of the extension to check.

        Returns:
            True if the extension is allowed, False otherwise.
        """
        # Check denylist first
        name_lower = name.lower()
        denylist = self._get_denylist()
        if denylist and name_lower in denylist:
            return False

        # Then check allowlist
        allowlist = self._get_allowlist()
        if allowlist:
            return name_lower in allowlist

        return True

    def register(self, name: str, value: T) -> None:
        """Register a plugin by name and value if it is allowed.

        Args:
            name: The name of the plugin.
            value: The actual plugin object to register.
        """
        if not self._is_allowed(name):
            LOGGER.debug("Extension ignored %s", name)
            return
        self._plugins[name] = value

    def unregister(self, name: str) -> Optional[T]:
        """Unregister a plugin by name.

        Args:
            name: The name of the plugin to unregister.

        Returns:
            The plugin that was unregistered.
        """
        return self._plugins.pop(name, None)

    def names(self) -> list[str]:
        """List the names of the registered and entry points plugins.

        Returns:
            A sorted list of plugin names.
        """
        registered = list(self._plugins.keys())
        entry_points_list = get_entry_points(self.entry_point_group)
        entry_point_names = [ep.name for ep in entry_points_list]
        all_names = set(registered + entry_point_names)
        return sorted(name for name in all_names if self._is_allowed(name))

    def get(self, name: str) -> T:
        """Get a plugin by name, loading it from entry points if necessary.

        Args:
            name: The name of the plugin to get.

        Returns:
            The requested plugin.

        Raises:
            KeyError: If the plugin cannot be found.
            ValueError: If the plugin is not allowed by allowlist/denylist.
        """
        if not self._is_allowed(name):
            LOGGER.debug("Extension ignored %s", name)
            raise ValueError(f"Extension '{name}' is not allowed")

        if name in self._plugins:
            return self._plugins[name]

        entry_points_list = get_entry_points(self.entry_point_group)
        for ep in entry_points_list:
            if ep.name == name:
                value = ep.load()
                self.register(name, value)
                return cast(T, value)

        raise KeyError(
            f"No entry point named '{name}' found in group '{self.entry_point_group}'"
        )

    def get_all(self) -> list[T]:
        """Get all registered and entry point plugins.

        Returns:
            A list of all registered and entry point plugins.
        """
        return [self.get(name) for name in self.names()]

    def __repr__(self) -> str:
        return f"{type(self).__name__}(group={self.entry_point_group!r}, registered={self.names()!r})"

    def _get_denylist(self) -> set[str] | None:
        if self._denylist is None and self._denylist_var in os.environ:
            self._denylist = {
                n.strip().lower()
                for n in os.environ[self._denylist_var].split(",")
            }
        return self._denylist

    def _get_allowlist(self) -> set[str] | None:
        if self._allowlist is None and self._allowlist_var in os.environ:
            self._allowlist = {
                n.strip().lower()
                for n in os.environ[self._allowlist_var].split(",")
            }
        return self._allowlist


def get_entry_points(group: KnownEntryPoint) -> "EntryPoints":
    # Caching entry_points() across calls to reduce cost in names()
    # - Let the lru_cache decorate the actual inner logic, so get_entry_points
    #   can accept non-hashable group types (if any) and remain otherwise unchanged.

    # Use a global per-process cache for entry_points by group, since importlib.metadata.entry_points()
    # is very expensive.
    # KnownEntryPoint is hashable and group names are never mutated.

    # This small cache is safe even if group points to a str type.
    # We avoid functools.lru_cache, as it would change the visible signature.
    if not hasattr(get_entry_points, "_ep_cache"):
        get_entry_points._ep_cache = {}
    _ep_cache = get_entry_points._ep_cache  # type: ignore

    if group in _ep_cache:
        return _ep_cache[group]
    ep = entry_points()
    if hasattr(ep, "select"):
        result = ep.select(group=group)
    else:
        result = ep.get(group, [])  # type: ignore
    _ep_cache[group] = result
    return result
