"""Database initialization and Supabase client helpers.

Includes a compatibility shim for the realtime dependency expecting
`websockets.asyncio.client`. We import our shim early so that if the
package layout is missing that namespace, the shim provides it before
`supabase` (and its `realtime` dependency) import executes.
"""

# Import websockets shim (safe no-op if not needed)
try:  # pragma: no cover - defensive
    import app.vendor.websockets_asyncio_shim  # noqa: F401
except Exception:  # pragma: no cover
    pass

# Compatibility patch: older supabase/gotrue stack passes 'proxy=' into
# httpx.Client which newer httpx versions (>0.25) no longer accept.
try:  # pragma: no cover - defensive
    import httpx  # type: ignore
    import inspect
    if 'proxy' not in inspect.signature(httpx.Client.__init__).parameters:
        _orig_init = httpx.Client.__init__
        def _patched_init(self, *args, proxy=None, **kwargs):  # noqa: D401
            if proxy is not None and 'proxies' not in kwargs:
                # Map deprecated single proxy kw to modern 'proxies' dict/string
                kwargs['proxies'] = proxy
            return _orig_init(self, *args, **kwargs)
        httpx.Client.__init__ = _patched_init  # type: ignore
except Exception:  # pragma: no cover
    pass

from supabase import create_client, Client
from app.core.config import settings
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Supabase client
supabase: Optional[Client] = None

async def init_db() -> None:
    """Initialize database connection.

    Does a lightweight select to validate credentials. Failures are logged
    but not raised so the application can still start (endpoints using the
    database will raise at access time via get_supabase()).
    """
    global supabase
    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
        )
        _ = supabase.table("app_admins").select("email").limit(1).execute()
        logger.info("Database connection established successfully")
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception("Failed to initialize database: %s", exc)
        supabase = None

def get_supabase() -> Client:
    """Return initialized Supabase client or raise clear runtime error."""
    if supabase is None:
        raise RuntimeError("Supabase client not initialized. Call init_db() earlier in startup.")
    return supabase

# Database helper functions
async def execute_query(
    table: str,
    operation: str,
    data: Optional[Dict[str, Any]] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a database operation with structured response.

    Returns
    -------
    dict
        {"success": bool, "data": Any | None, "error": str | None}
    """
    try:
        db = get_supabase()
        query = db.table(table)

        if filters and operation in {"select", "update", "delete"}:
            for key, value in filters.items():
                query = query.eq(key, value)

        if operation == "select":
            result = query.execute()
        elif operation == "insert":
            result = query.insert(data or {}).execute()
        elif operation == "update":
            result = query.update(data or {}).execute()
        elif operation == "delete":
            result = query.delete().execute()
        else:
            return {"success": False, "error": f"Unsupported operation: {operation}"}

        return {"success": True, "data": result.data}
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception("Database query failed: %s", exc)
        return {"success": False, "error": str(exc)}