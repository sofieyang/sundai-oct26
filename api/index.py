import sys
from pathlib import Path

# Ensure project root is on sys.path so we can import the app
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the FastAPI application instance
from app.server import app  # noqa: E402

# Vercel Python runtime looks for a top-level variable named `app`.
# Expose FastAPI instance as `app`.


