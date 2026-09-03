"""render — build docs/index.md from data/raw/. Offline, deterministic.

Standalone:  python py/step_render.py
Via main.py: python main.py            (default step)

Writes a Jekyll page (front matter + body) for the respec-github-pages
layout that already ships in docs/_layouts/respec.html — that layout and the
Gemfile/CSS around it are untouched template infrastructure; only the front
matter values and the body content below are project-specific, and every
table in the body is derived from a data/raw/ file at build time. See
PRIMER.md A2 for which file feeds which section.
"""

from __future__ import annotations

import ast
import html
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fdo_squirrel_spec_utils import (
    DOCS,
    RAW_FILES,
    RELEASE,
    SOURCE_REPO,
    content_fingerprint,
    ensure_dirs,
    write_text,
)

SPEC_SHORT_NAME = "fdo-squirrel-spec"
SPEC_TITLE = "MD.cff — Metadata Format for FDO Squirrel"
REPO_URL = "https://github.com/FDOx-squirrel/fdo-squirrel-spec"

# The respec.html layout does `JSON.parse(`{{ page.respec }}`)` inside a JS
# template literal, so this only needs to be valid JSON once whitespace is
# collapsed — the exact YAML folding of the front matter block doesn't matter.
RESPEC_CONFIG = {
    "name": SPEC_SHORT_NAME,
    "status": "unofficial",
    "latest": "https://fdox-squirrel.github.io/fdo-squirrel-spec/",
    "repository": REPO_URL,
    "issues": f"{REPO_URL}/issues",
    "group": {
        "name": "Research Squirrel Engineers",
        "url": "https://github.com/Research-Squirrel-Engineers",
        "list": "",
        "patentUri": "",
    },
    "editors": [
        {
            "name": "Florian Thiery",
            "company": "LEIZA / Research Squirrel Engineers",
            "url": "https://github.com/Research-Squirrel-Engineers",
        }
    ],
    "bibliography": {},
}


# --------------------------------------------------------------------------
# Extraction — each function reads exactly one data/raw/ file
# --------------------------------------------------------------------------

def load_schema() -> dict:
    return yaml.safe_load(RAW_FILES["schema"].read_text(encoding="utf-8"))


def load_crosswalk() -> dict:
    return yaml.safe_load(RAW_FILES["crosswalk"].read_text(encoding="utf-8"))


def load_classification() -> dict:
    return yaml.safe_load(RAW_FILES["classification"].read_text(encoding="utf-8"))


def load_zip_member_candidates() -> dict:
    """Pull the ZIP-matching constants out of package_source.py without executing it."""
    src = RAW_FILES["package_source"].read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name in ("DEFAULT_MD_MEMBER_CANDIDATES", "DEFAULT_CFF_MEMBER_CANDIDATES"):
                out[name] = ast.literal_eval(node.value)
    return out


def load_ttl_prefixes() -> list[tuple[str, str]]:
    """@prefix declarations only — the instance body is a known-flawed demo
    (mixes SoftwareFDO and 3DDataFDO fields), so it is not rendered here."""
    text = RAW_FILES["example_ttl"].read_text(encoding="utf-8")
    return re.findall(r"@prefix\s+([\w-]+):\s+<([^>]+)>", text)


# --------------------------------------------------------------------------
# HTML fragment builders (plain <table>/<p class="note">, no custom CSS —
# respec.css already styles both)
# --------------------------------------------------------------------------

def esc(s) -> str:
    return html.escape(str(s), quote=True)


def properties_table(schema: dict) -> str:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    rows = []
    for name, spec in props.items():
        ptype = spec.get("type", spec.get("enum", "—"))
        if isinstance(ptype, list):
            ptype = ", ".join(str(t) for t in ptype)
        desc = spec.get("description", "")
        req = "yes" if name in required else "no"
        rows.append(
            f"<tr><td><code>{esc(name)}</code></td><td>{esc(ptype)}</td>"
            f"<td>{esc(req)}</td><td>{esc(desc)}</td></tr>"
        )
    return (
        "<table>"
        "<thead><tr><th>Property</th><th>Type</th><th>Required</th><th>Description</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def fdo_classes_list(schema: dict) -> str:
    classes = schema.get("properties", {}).get("fdo_type", {}).get("enum", [])
    items = "".join(f"<li><code>{esc(c)}</code></li>" for c in classes)
    return f"<ul>{items}</ul>"


def classification_table(classification: dict) -> str:
    rows = []
    for fdo_class, body in classification.get("fdo_classes", {}).items():
        default_role = body.get("default_role", "—")
        for rule in body.get("rules", []):
            match = rule.get("match", {})
            match_str = "; ".join(f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in match.items())
            rows.append(
                f"<tr><td><code>{esc(fdo_class)}</code></td><td>{esc(match_str)}</td>"
                f"<td>{esc(rule.get('role', default_role))}</td></tr>"
            )
    return (
        "<table>"
        "<thead><tr><th>FDO class</th><th>Match rule</th><th>Assigned role</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def crosswalk_prefixes_table(crosswalk: dict) -> str:
    rows = [
        f"<tr><td><code>{esc(p)}</code></td><td><code>{esc(uri)}</code></td></tr>"
        for p, uri in crosswalk.get("prefixes", {}).items()
    ]
    return (
        "<table><thead><tr><th>Prefix</th><th>Namespace</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def crosswalk_handlers_list(crosswalk: dict) -> str:
    items = []
    for name, body in crosswalk.get("handlers", {}).items():
        desc = body.get("description", "")
        items.append(f"<li><dfn>{esc(name)}</dfn> — {esc(desc)}</li>")
    return f"<ul>{''.join(items)}</ul>"


def zip_structure_section(candidates: dict) -> str:
    md_c = candidates.get("DEFAULT_MD_MEMBER_CANDIDATES", [])
    cff_c = candidates.get("DEFAULT_CFF_MEMBER_CANDIDATES", [])
    return f"""<p>A package is a ZIP archive. There is no fixed internal layout — the loader
identifies the metadata files by matching candidate names against the archive
members, in this order: (1) an exact-path match if one was configured,
(2) an exact filename match against the candidate list, (3) an unambiguous
<code>endswith</code> match. More than one match at the same step is a hard
error rather than a guess.</p>
<table>
<thead><tr><th>Role</th><th>Candidate filenames</th></tr></thead>
<tbody>
<tr><td>MD.cff (FDO metadata)</td><td>{esc(', '.join(md_c))}</td></tr>
<tr><td>CITATION.cff</td><td>{esc(', '.join(cff_c))}</td></tr>
</tbody>
</table>
<p class="note">Both files may also sit at the ZIP root as loose files instead
of inside an archive, and either may be supplied by URL (a remote ZIP is
downloaded and read the same way).</p>"""


def vocabularies_section(prefixes: list[tuple[str, str]]) -> str:
    rows = "".join(f"<tr><td><code>{esc(p)}</code></td><td><code>{esc(uri)}</code></td></tr>" for p, uri in prefixes)
    return f"""<p class="note">The vocabularies below are the namespaces declared in
fdo-squirrel's demo instance. That instance is known to mix fields from more
than one FDO class and is <strong>not</strong> reproduced here as a worked
example for that reason — only the namespace list is derived from it.</p>
<table><thead><tr><th>Prefix</th><th>Namespace</th></tr></thead>
<tbody>{rows}</tbody></table>"""


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def front_matter() -> str:
    # Same shape as the template's own docs/index.md: `respec: >` followed by
    # the JSON, indented two spaces under the key.
    raw_json = json.dumps(RESPEC_CONFIG, indent=2, ensure_ascii=False)
    indented = "\n".join("  " + line for line in raw_json.splitlines())
    return f"""---
layout: respec
title: {SPEC_TITLE}
respec: >
{indented}
---"""


def body() -> str:
    schema = load_schema()
    crosswalk = load_crosswalk()
    classification = load_classification()
    candidates = load_zip_member_candidates()
    ttl_prefixes = load_ttl_prefixes()

    provenance_rows = "".join(
        f"<tr><td><code>{esc(key)}</code></td><td><code>{esc(content_fingerprint(path))}</code></td></tr>"
        for key, path in RAW_FILES.items()
    )

    return f"""
<section id="abstract">
<p>This document specifies <dfn>MD.cff</dfn>, the metadata format read by
<a href="{esc(SOURCE_REPO)}">fdo-squirrel</a> to turn a data package into a
FAIR Digital Object (FDO): the package's ZIP structure, the MD.cff schema
itself, the crosswalk to RDF, and the rules used to classify files inside a
package by role.</p>
</section>

<section id="sotd">
<p>This is generated documentation, not a W3C process document. Every table
below is built at render time from files copied out of fdo-squirrel (see the
provenance table at the end); it is not hand-maintained prose and can go
stale exactly when fdo-squirrel's schema does — run
<code>python main.py fetch</code> to refresh, then <code>python main.py</code>
to rebuild this page.</p>
</section>

<section>
<h2>Package structure</h2>
{zip_structure_section(candidates)}
</section>

<section>
<h2>MD.cff schema</h2>
<p>MD.cff version <code>{esc(schema.get('properties', {}).get('md_cff_version', {}).get('const', '?'))}</code>.
Target FDO classes:</p>
{fdo_classes_list(schema)}
<h3>Properties</h3>
{properties_table(schema)}
</section>

<section>
<h2>File classification rules</h2>
<p>Once a package is identified as belonging to an FDO class, each file inside
it is assigned a role by matching against ordered rules for that class.</p>
{classification_table(classification)}
</section>

<section>
<h2>Crosswalk to RDF</h2>
<p>MD.cff fields are lifted to RDF (DCAT/DCT, GeoSPARQL, CodeMeta, FDO) using
named handlers over the following namespaces:</p>
{crosswalk_prefixes_table(crosswalk)}
<h3>Handlers</h3>
{crosswalk_handlers_list(crosswalk)}
</section>

<section>
<h2>Vocabularies in the example instance</h2>
{vocabularies_section(ttl_prefixes)}
</section>

<section id="conformance">
<p>This document has no independent conformance requirements: an MD.cff file
conforms if and only if it validates against the JSON Schema shipped in
<code>data/raw/MD.cff-schema.yaml</code> in this repository.</p>
</section>

<section class="appendix">
<h2>Provenance</h2>
<p>Built {esc(RELEASE)} from these files (sha256, first 12 hex digits):</p>
<table><thead><tr><th>Source</th><th>Fingerprint</th></tr></thead>
<tbody>{provenance_rows}</tbody></table>
</section>
"""


def run() -> None:
    ensure_dirs()
    out = DOCS / "index.md"
    write_text(out, front_matter() + "\n" + body())
    print(f"  wrote {out.relative_to(out.parents[1])}")


if __name__ == "__main__":
    run()
