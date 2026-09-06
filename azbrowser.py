"""AZBrowser shim. Prefer `python -m azbrowser` or the `azbrowser` console script."""

from azbrowser.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
