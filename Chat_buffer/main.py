"""
Deprecated: use the unified assistant API instead.

  cd <project root>
  python api/main.py

The old /chat endpoint only buffered messages without memory routing.
"""

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    os.chdir(root)

    print("Chat_buffer is deprecated. Starting unified API (api/main.py)...")

    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
