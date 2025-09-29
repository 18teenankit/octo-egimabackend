"""Runtime compatibility patches applied very early in startup.

Currently addresses:
1. httpx.Client missing legacy 'proxy' kw expected by gotrue/supabase stack.
2. (Optional) websockets realtime shim if needed (already handled elsewhere).
"""

from __future__ import annotations

import inspect
import logging

logger = logging.getLogger(__name__)

# Patch httpx.Client to accept a deprecated 'proxy=' kw (mapped to 'proxies').
try:  # pragma: no cover
    import httpx  # type: ignore

    if 'proxy' not in inspect.signature(httpx.Client.__init__).parameters:
        _orig_init = httpx.Client.__init__

        def _patched_init(self, *args, proxy=None, **kwargs):  # noqa: D401
            if proxy is not None and 'proxies' not in kwargs:
                kwargs['proxies'] = proxy
            return _orig_init(self, *args, **kwargs)

        httpx.Client.__init__ = _patched_init  # type: ignore[attr-defined]
        logger.info("Applied httpx.Client proxy compatibility patch")
except Exception as exc:  # pragma: no cover
    logger.debug("Skipping httpx proxy patch: %s", exc)

# Patch gotrue SyncGoTrueBaseAPI to ignore legacy 'proxy' kw when constructing httpx Client.
try:  # pragma: no cover
    import gotrue._sync.gotrue_base_api as _gba  # type: ignore
    _orig_gotrue_init = _gba.SyncGoTrueBaseAPI.__init__
    def _gba_init(self, *args, **kwargs):
        kwargs.pop('proxy', None)  # discard unsupported kw for modern httpx
        return _orig_gotrue_init(self, *args, **kwargs)
    _gba.SyncGoTrueBaseAPI.__init__ = _gba_init  # type: ignore
    logger.info("Applied gotrue SyncGoTrueBaseAPI proxy kw discard patch")
except Exception as exc:  # pragma: no cover
    logger.debug("Skipping gotrue proxy patch: %s", exc)
