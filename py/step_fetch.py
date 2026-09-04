"""fetch — refresh data/raw/ from the upstream repositories.

Standalone:  python py/step_fetch.py
Via main.py: python main.py fetch

This is the ONLY step that touches the network. It never runs as part of the
default `python main.py` pipeline (see A3 in PRIMER.md) — run it by hand when
you want the spec to catch up with upstream, then run `python main.py` to
re-render docs/index.md from the refreshed copies.

Two sources as of S2/S3 (PRIMER A4, 2026-09-04): fdo-squirrel itself, pinned
to a stable tag (UPSTREAM_REF), and fdo-squirrel-registry's harvested
fdo-metadata.ttl instances for the worked examples, unpinned on `main` so
they stay current. See UPSTREAM_SOURCES in fdo_squirrel_spec_utils.py for the
exact file list.

Reuse means copying, not referencing: this writes plain files into
data/raw/, it does not make step_render.py reach out over the network itself.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fdo_squirrel_spec_utils import UPSTREAM_SOURCES, ensure_dirs


def raw_base(repo: str, ref: str) -> str:
    return repo.replace("github.com", "raw.githubusercontent.com") + f"/{ref}/"


def fetch_one(base: str, upstream_path: str, dest: Path) -> None:
    url = base + upstream_path
    req = urllib.request.Request(url, headers={"User-Agent": "fdo-squirrel-spec/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"  fetched {upstream_path} -> {dest.relative_to(dest.parents[2])} ({len(data)} bytes)")


def run() -> None:
    ensure_dirs()
    for source_name, source in UPSTREAM_SOURCES.items():
        repo = source["repo"]
        ref = source["ref"]
        print(f"Fetching from {repo} @ {ref}")
        base = raw_base(repo, ref)
        for upstream_path, dest in source["files"].values():
            fetch_one(base, upstream_path, dest)
    print("Done. Review the diff, then run: python main.py")


if __name__ == "__main__":
    run()
