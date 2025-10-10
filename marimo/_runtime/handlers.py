# Copyright 2024 Marimo. All rights reserved.
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from marimo import _loggers
from marimo._messaging.ops import Interrupted
from marimo._runtime.context import get_context
from marimo._runtime.context.kernel_context import KernelRuntimeContext
from marimo._runtime.control_flow import MarimoInterrupt

LOGGER = _loggers.marimo_logger()

if TYPE_CHECKING:
    from marimo._runtime.runtime import Kernel


def construct_interrupt_handler(
    context: KernelRuntimeContext,
) -> Callable[[int, Any], None]:
    def interrupt_handler(signum: int, frame: Any) -> None:
        """Tries to interrupt the kernel."""
        del signum
        del frame

        LOGGER.info("Interrupt request received")
        # TODO(akshayka): if kernel is in `run` but not executing,
        # it won't be interrupted, which isn't right ... but the
        # probability of that happening is low.
        if context.execution_context is not None:
            Interrupted().broadcast()
            raise MarimoInterrupt

    return interrupt_handler


def construct_sigterm_handler(kernel: "Kernel") -> Callable[[int, Any], None]:
    del kernel

    # Using a function attribute instead of a dataclass instance
    # avoids a per-handler-class creation and keeps the "once only" flag
    # fast and memory-efficient.
    def sigterm_handler(signum: int, frame: Any) -> None:
        """Cleans up the kernel and exits."""
        del signum
        del frame

        if getattr(sigterm_handler, "_shutting_down", False):
            # give previous SIGTERM a chance to quit ... makes
            # sure this method is reentrant
            return
        sigterm_handler._shutting_down = True

        get_context().virtual_file_registry.shutdown()
        # Force this process to exit.
        #
        # We use os._exit() instead of sys.exit() because we don't want the
        # child process to also run atexit handlers, which may result in
        # undefined behavior. Using sys.exit() on Linux sometimes causes
        # the parent process to hang on shutdown, leading to orphaned
        # processes and port.
        #
        # TODO(akshayka): The Python docs say this method is appropriate
        # for processes created with fork(), but they don't say anything
        # about processes made with spawn. macOS and Windows default to
        # spawn. If we have further issues with clean exits, we might
        # investigate here.
        #
        # https://docs.python.org/3/library/os.html#os._exit
        # https://www.unixguide.net/unix/programming/1.1.3.shtml
        os._exit(0)

    return sigterm_handler
