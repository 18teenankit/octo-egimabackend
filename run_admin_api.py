"""Unified Admin API launcher.

Ensures project root and backend added to sys.path, applies monkeypatches
early, then runs uvicorn for main_admin:app.
"""
from __future__ import annotations
import os, sys, pathlib, uvicorn

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Apply patches if any
from app.core import monkeypatches  # noqa: F401

def main():
    os.chdir(BACKEND)
    uvicorn.run(
        'main_admin:app',
        host=os.environ.get('ADMIN_API_HOST', '0.0.0.0'),
        port=int(os.environ.get('ADMIN_API_PORT', '8001')),
        reload=os.environ.get('ENVIRONMENT', 'development') == 'development',
        env_file=str(BACKEND / '.env'),
    )

if __name__ == '__main__':
    main()
