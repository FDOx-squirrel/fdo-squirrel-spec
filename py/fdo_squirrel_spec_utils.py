"""Shared constants, paths and canonical writers for fdo-squirrel-spec.

Kept dependency-free (stdlib only) except for PyYAML, which the render step
needs to read data/raw/*.yaml. No datetime.now() anywhere: RELEASE is the one
place a date is allowed to appear in generated output.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs"
DIST = ROOT / "dist"

# --------------------------------------------------------------------------
# Release marker
# --------------------------------------------------------------------------
# Bump by hand when the spec content moves forward a step. Never derived from
# the clock, so a rebuild with no source change is byte-identical.
RELEASE = "2026-09-03"

# The four raw sources this repo currently understands. step_fetch.py refreshes
# them from upstream; step_render.py reads them and nothing else network-side.
SOURCE_REPO = "https://github.com/Research-Squirrel-Engineers/fdo-squirrel"
RAW_FILES = {
    "schema": DATA_RAW / "MD.cff-schema.yaml",
    "crosswalk": DATA_RAW / "crosswalk_md_cff_to_rdf.yaml",
    "classification": DATA_RAW / "classification_rules.yaml",
    "example_ttl": DATA_RAW / "fdo-metadata.ttl",
    "package_source": DATA_RAW / "package_source.py",
}
# Path of each file inside the upstream repo, for step_fetch.py.
RAW_FILES_UPSTREAM_PATH = {
    "schema": "schemas/md_cff/MD.cff-schema.yaml",
    "crosswalk": "schemas/md_cff/crosswalk_md_cff_to_rdf.yaml",
    "classification": "fdo/classification_rules.yaml",
    "example_ttl": "fdo/fdo-metadata.ttl",
    "package_source": "ingest/package_source.py",
}


def ensure_dirs() -> None:
    for d in (DATA_RAW, DOCS, DIST):
        d.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    """Canonical text writer: LF line endings, trailing newline, UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, obj) -> None:
    write_text(path, json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2))


def content_fingerprint(path: Path) -> str:
    """Short sha256 of a file's bytes, used to note provenance in generated output."""
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
