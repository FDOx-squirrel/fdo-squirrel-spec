"""fetch — refresh data/raw/ from the upstream fdo-squirrel repository.

Standalone:  python py/step_fetch.py
Via main.py: python main.py fetch

This is the ONLY step that touches the network. It never runs as part of the
default `python main.py` pipeline (see A3 in PRIMER.md) — run it by hand when
you want the spec to catch up with upstream, then run `python main.py` to
re-render docs/index.html from the refreshed copies.

Reuse means copying, not referencing: this writes plain files into
data/raw/, it does not make step_render.py reach out over the network itself.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fdo_squirrel_spec_utils import (
    RAW_FILES,
    RAW_FILES_UPSTREAM_PATH,
    SOURCE_REPO,
    ensure_dirs,
)

# Pin a ref so a fetch is reproducible until someone deliberately moves it.
# Update alongside RELEASE in fdo_squirrel_spec_utils.py when you bump it.
UPSTREAM_REF = "main"
RAW_BASE = SOURCE_REPO.replace("github.com", "raw.githubusercontent.com") + f"/{UPSTREAM_REF}/"


def fetch_one(key: str) -> None:
    upstream_path = RAW_FILES_UPSTREAM_PATH[key]
    url = RAW_BASE + upstream_path
    dest = RAW_FILES[key]
    req = urllib.request.Request(url, headers={"User-Agent": "fdo-squirrel-spec/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"  fetched {upstream_path} -> {dest.relative_to(dest.parents[2])} ({len(data)} bytes)")


def run() -> None:
    ensure_dirs()
    print(f"Fetching from {SOURCE_REPO} @ {UPSTREAM_REF}")
    for key in RAW_FILES:
        fetch_one(key)
    print("Done. Review the diff, then run: python main.py")


if __name__ == "__main__":
    run()
