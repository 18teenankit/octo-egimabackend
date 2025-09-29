"""Shim to provide websockets.asyncio.client.ClientConnection expected by realtime 1.0.6.

The realtime package imports:
    from websockets.asyncio.client import ClientConnection

In websockets 12.0 the public layout changed; the asyncio namespace package
may not be present in certain distributions. We map the expected symbol to
websockets.client.connect return type by creating a lightweight proxy.

If a future upgrade provides the proper package, this shim becomes a no-op.
"""
from __future__ import annotations

try:
    # If the module path exists in future versions, just rely on it.
    from websockets.asyncio.client import ClientConnection as _ClientConnection  # type: ignore
    ClientConnection = _ClientConnection  # noqa
except Exception:  # pragma: no cover - fallback path
    import websockets
    from typing import Any, Awaitable

    class ClientConnection:  # type: ignore
        """Minimal stand‑in that wraps a connected websocket.

        Only attributes used by realtime should be proxied. Extend as needed.
        """
        def __init__(self, ws):
            self._ws = ws

        async def send(self, data: Any):  # noqa: D401
            return await self._ws.send(data)

        async def recv(self) -> Any:  # noqa: D401
            return await self._ws.recv()

        async def close(self, code: int = 1000, reason: str | None = None):
            await self._ws.close(code=code, reason=reason or "")

    async def connect(*args, **kwargs) -> ClientConnection:
        ws = await websockets.connect(*args, **kwargs)  # type: ignore
        return ClientConnection(ws)
