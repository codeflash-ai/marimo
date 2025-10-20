# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import signal
from typing import Any

_SIGTERM = signal.SIGTERM

_SIGINT = signal.SIGINT

_getsignal = signal.getsignal


def restore_signals() -> None:
    # Restore the system default signal handlers.
    #
    # The server process may register signal handlers (uvicorn does this),
    # which we definitely don't want! Otherwise a SIGTERM to this process
    # would be rerouted to the server.
    #
    # See https://github.com/tiangolo/fastapi/discussions/7442#discussioncomment-5141007  # noqa: E501
    signal.set_wakeup_fd(-1)

    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def get_signals() -> dict[int, Any]:
    return {
        _SIGTERM: _getsignal(_SIGTERM),
        _SIGINT: _getsignal(_SIGINT),
    }
