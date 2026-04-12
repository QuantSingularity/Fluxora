"""
Fluxora backend entry point.

Run from the ``backend/`` directory:
    python main.py
or via uvicorn:
    uvicorn app.main:app --reload

The project root (parent of ``backend/``) is inserted into ``sys.path``
here as well so that ``ml_core`` is importable even when this script is
executed directly.
"""

import os
import sys

# Ensure project root is importable (ml_core lives one level above backend/)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.main import app  # noqa: F401, E402

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        workers=int(os.getenv("API_WORKERS", "1")),
        reload=os.getenv("ENV", "production") == "development",
    )
