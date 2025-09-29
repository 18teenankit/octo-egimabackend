"""Unified backend launcher.

Ensures project root and backend added to sys.path, applies monkeypatches
early, then runs uvicorn. Use instead of ad-hoc task commands.
"""
from __future__ import annotations
import os, sys, pathlib, uvicorn

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Apply patches
from app.core import monkeypatches  # noqa: F401

def main():
    os.chdir(BACKEND)
    # On Windows, uvicorn reload can cause import issues with native extensions.
    # Default to no-reload on Windows unless FORCE_RELOAD=true is set.
    env = os.environ.get('ENVIRONMENT', 'development')
    force_reload = os.environ.get('FORCE_RELOAD', '').lower() == 'true'
    is_windows = os.name == 'nt'
    reload_enabled = (env == 'development' and not is_windows) or force_reload

    uvicorn.run(
        'main:app',
        host=os.environ.get('BACKEND_HOST', '0.0.0.0'),
        port=int(os.environ.get('BACKEND_PORT', '8000')),
        reload=reload_enabled,
        env_file=str(BACKEND / '.env'),
    )

if __name__ == '__main__':
    main()