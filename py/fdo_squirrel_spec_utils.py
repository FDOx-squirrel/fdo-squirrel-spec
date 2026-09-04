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
RELEASE = "2026-09-04"

# --------------------------------------------------------------------------
# Upstream sources
# --------------------------------------------------------------------------
# fdo-squirrel moved from Research-Squirrel-Engineers to FDOx-squirrel; the
# old org still 200s (GitHub's soft-redirect page) but is not the canonical
# URL any more (Befund 2026-09-04, PRIMER A1).
SOURCE_REPO = "https://github.com/FDOx-squirrel/fdo-squirrel"
# Second source, added in S2 for the worked examples (PRIMER A4, 2026-09-04):
# real, harvested fdo-metadata.ttl instances, not the mixed-class demo file
# that used to ship inside fdo-squirrel itself.
SOURCE_REPO_REGISTRY = "https://github.com/FDOx-squirrel/fdo-squirrel-registry"

# fdo-squirrel now tags releases (S3, PRIMER A4 2026-09-04): pin to the latest
# stable tag instead of `main`, so a fetch is reproducible until someone
# deliberately bumps it. fdo-squirrel-registry does not tag; its harvest is
# meant to stay current, so that source stays on `main`.
UPSTREAM_REF = "v0.3.1"
REGISTRY_REF = "main"

# One entry per source repo: which files to pull, and where they land under
# data/raw/. step_fetch.py walks this; step_render.py only ever reads the
# local paths on the right via RAW_FILES.
UPSTREAM_SOURCES = {
    "fdo-squirrel": {
        "repo": SOURCE_REPO,
        "ref": UPSTREAM_REF,
        "files": {
            "schema": ("schemas/md_cff/MD.cff-schema.yaml", DATA_RAW / "MD.cff-schema.yaml"),
            "crosswalk": ("schemas/md_cff/crosswalk_md_cff_to_rdf.yaml", DATA_RAW / "crosswalk_md_cff_to_rdf.yaml"),
            "classification": ("fdo/classification_rules.yaml", DATA_RAW / "classification_rules.yaml"),
            "package_source": ("ingest/package_source.py", DATA_RAW / "package_source.py"),
            # NOTE: fdo/fdo-metadata.ttl (the demo instance) is deliberately
            # NOT fetched any more. It mixes SoftwareFDO and 3DDataFDO fields
            # (Befund 2026-09-03) and its only use here was namespace
            # extraction, a job the two real worked examples below now do
            # better (PRIMER A4, 2026-09-04).
        },
    },
    "fdo-squirrel-registry": {
        "repo": SOURCE_REPO_REGISTRY,
        "ref": REGISTRY_REF,
        "files": {
            # Two real, SHACL-gate-passed harvested instances, one per FDO
            # class currently available in the registry (no AnalysisFDO
            # instance exists yet). Picked for being compact enough to show
            # in full and for showing distinct crosswalk paths (ORCID
            # creators vs. local person IRIs; geo+temporal vs. none).
            "example_software": ("data/raw/fdo/18369126/fdo-metadata.ttl", DATA_RAW / "examples" / "software-fdo.ttl"),
            "example_3d": ("data/raw/fdo/18744133/fdo-metadata.ttl", DATA_RAW / "examples" / "3d-data-fdo.ttl"),
        },
    },
}

# Flattened view for step_render.py / the provenance table: local key -> path.
RAW_FILES = {
    key: dest
    for source in UPSTREAM_SOURCES.values()
    for key, (_, dest) in source["files"].items()
}

# Which FDO class each worked example demonstrates, and the record's DOI, for
# the "worked examples" section. Kept next to RAW_FILES rather than derived
# from the TTL, since the class is exactly what we chose the record *for*.
EXAMPLE_RECORDS = {
    "example_software": {
        "fdo_class": "fdo:SoftwareFDO",
        "doi": "https://doi.org/10.5281/zenodo.18369125",
        "harvested_from": f"{SOURCE_REPO_REGISTRY}/blob/{REGISTRY_REF}/data/raw/fdo/18369126/fdo-metadata.ttl",
    },
    "example_3d": {
        "fdo_class": "fdo:3DDataFDO",
        "doi": "https://doi.org/10.5281/zenodo.18724635",
        "harvested_from": f"{SOURCE_REPO_REGISTRY}/blob/{REGISTRY_REF}/data/raw/fdo/18744133/fdo-metadata.ttl",
    },
}

# Canonical prefix bindings, copied (not imported) from
# fdo-squirrel-registry/py/registry_utils.py PREFIXES (as of 2026-09-04).
# Used only to repair harvested TTL that uses a prefix but never declares it
# (see py/example_repair.py) - never to invent content, only to write down a
# binding the generator itself already uses elsewhere.
EXAMPLE_PREFIXES: dict[str, str] = {
    "bibo": "http://purl.org/ontology/bibo/",
    "cff": "https://citation-file-format.github.io/terms/",
    "codemeta": "https://codemeta.github.io/terms/",
    "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    "crmdig": "http://www.ics.forth.gr/isl/CRMdig/",
    "crmgeo": "http://www.ics.forth.gr/isl/CRMgeo/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "edtf": "http://id.loc.gov/datatypes/edtf/",
    "fdo": "https://w3id.org/fdo-squirrel/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "geosparql": "http://www.opengis.net/ont/geosparql#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "prov": "http://www.w3.org/ns/prov#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "https://schema.org/",
    "sf": "http://www.opengis.net/ont/sf#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "time": "http://www.w3.org/2006/time#",
    "wd": "http://www.wikidata.org/entity/",
    "wdt": "http://www.wikidata.org/prop/direct/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
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
