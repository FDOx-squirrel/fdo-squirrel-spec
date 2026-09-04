"""render — build docs/index.md from data/raw/. Offline, deterministic.

Standalone:  python py/step_render.py
Via main.py: python main.py            (default step)

Writes a Jekyll page (front matter + body) for the respec-github-pages
layout that already ships in docs/_layouts/respec.html — that layout and the
Gemfile/CSS around it are untouched template infrastructure; only the front
matter values and the body content below are project-specific, and every
table in the body is derived from a data/raw/ file at build time. See
PRIMER.md A2 for which file feeds which section.

The two worked examples (data/raw/examples/*.ttl) are parsed with rdflib
rather than by regex, because they are real harvested Turtle and one of them
is invalid as harvested (see example_repair.py) — a text-only extraction
would have to special-case that silently, a graph parse plus a declared
repair layer says so on the page instead.
"""

from __future__ import annotations

import ast
import html
import json
import re
import sys
from pathlib import Path

import rdflib
import yaml
from rdflib import RDF, RDFS, Namespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import example_repair
from fdo_squirrel_spec_utils import (
    DOCS,
    EXAMPLE_PREFIXES,
    EXAMPLE_RECORDS,
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

DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
SCHEMA = Namespace("https://schema.org/")
FDO = Namespace("https://w3id.org/fdo-squirrel/")
GEOSPARQL = Namespace("http://www.opengis.net/ont/geosparql#")

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
        "url": "https://github.com/FDOx-squirrel",
        "list": "",
        "patentUri": "",
    },
    "editors": [
        {
            "name": "Florian Thiery",
            "company": "LEIZA / Research Squirrel Engineers",
            "url": "https://github.com/FDOx-squirrel",
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


def load_example(key: str) -> tuple[rdflib.Graph, list[str]]:
    """Parse a harvested worked-example TTL, repairing known upstream defects
    in memory only (see example_repair.py). The file on disk is never
    touched, so content_fingerprint() always hashes the true harvested bytes."""
    text = RAW_FILES[key].read_text(encoding="utf-8")

    def try_parse(t: str) -> None:
        rdflib.Graph().parse(data=t, format="turtle")

    repaired_text, applied = example_repair.repair(text, try_parse, EXAMPLE_PREFIXES)
    g = rdflib.Graph()
    g.parse(data=repaired_text, format="turtle")
    return g, applied


def declared_prefixes(key: str) -> list[tuple[str, str]]:
    """@prefix declarations as actually written in the raw harvested file —
    not repaired, so a missing one shows up as missing here too."""
    text = RAW_FILES[key].read_text(encoding="utf-8")
    return re.findall(r"@prefix\s+([\w-]+):\s+<([^>]+)>", text)


# --------------------------------------------------------------------------
# HTML fragment builders (plain <table>/<p class="note">, no custom CSS —
# respec.css already styles both)
# --------------------------------------------------------------------------

def esc(s) -> str:
    if s is None:
        return "—"
    return html.escape(str(s), quote=True)


def humanize_bytes(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


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


def creator_name(g: rdflib.Graph, uri: rdflib.term.URIRef) -> str:
    name = g.value(uri, SCHEMA.name)
    return str(name) if name else str(uri)


def worked_example_section(key: str) -> str:
    record = EXAMPLE_RECORDS[key]
    g, repairs = load_example(key)
    subj = next(g.subjects(RDF.type, DCAT.Dataset), None)
    if subj is None:
        return f'<section><p class="note">Could not find a dcat:Dataset subject in {esc(key)}.</p></section>'

    title = g.value(subj, DCT.title)
    descriptions = [str(d) for d in g.objects(subj, DCT.description)]
    desc = descriptions[0] if descriptions else ""
    extra_desc_note = (
        f" ({len(descriptions) - 1} further description value(s) in this record, "
        "a data quality matter for fdo-squirrel-registry, not shown here)"
        if len(descriptions) > 1
        else ""
    )
    version = g.value(subj, DCT.hasVersion)
    license_ = g.value(subj, DCT.license)
    creators = [creator_name(g, c) for c in g.objects(subj, DCT.creator)]
    created = g.value(subj, DCT.created)
    modified = g.value(subj, DCT.modified)
    context = g.value(subj, FDO.context)
    geom = g.value(subj, GEOSPARQL.hasGeometry)
    wkt = g.value(geom, GEOSPARQL.asWKT) if geom else None
    temporal = g.value(subj, DCT.temporal)
    temporal_label = g.value(temporal, RDFS.label) if temporal else None

    dists = list(g.objects(subj, DCAT.distribution))
    total_bytes = sum(int(n) for d in dists if (n := g.value(d, DCAT.byteSize)) is not None)
    roles: dict[str, int] = {}
    for d in dists:
        r = g.value(d, FDO.role)
        r = str(r) if r else "?"
        roles[r] = roles.get(r, 0) + 1
    role_summary = ", ".join(f"{esc(k)}: {v}" for k, v in sorted(roles.items()))

    sample = dists[:3]
    sample_rows = "".join(
        f"<tr><td><code>{esc(g.value(d, FDO.path))}</code></td><td>{esc(g.value(d, FDO.role))}</td>"
        f"<td>{esc(g.value(d, DCAT.byteSize))}</td></tr>"
        for d in sample
    )
    more_note = (
        f'<p class="note">{len(dists) - len(sample)} further distribution(s) omitted here for '
        "readability — see the full record for the complete list.</p>"
        if len(dists) > len(sample)
        else ""
    )

    repair_note = ""
    if repairs:
        labels = ", ".join(esc(r.split(":", 1)[1]) for r in repairs)
        repair_note = f"""<p class="note"><strong>As harvested, this record is invalid Turtle:</strong>
it uses the prefix(es) <code>{labels}</code> without ever declaring them — a defect in the
fdo-squirrel version that produced it (fixed in later versions, see PRIMER.md A1). The file
on disk in this repository under <code>data/raw/examples/</code> is the unmodified harvested
original; the missing <code>@prefix</code> line(s) were added only in memory, the same way
fdo-squirrel-registry's own repair layer does it, to render this section.</p>"""

    return f"""
<section>
<h3>{esc(record['fdo_class'])} — {esc(title)}</h3>
{repair_note}
<p>{esc(desc)}{extra_desc_note}</p>
<table>
<tbody>
<tr><td>Version</td><td>{esc(version)}</td></tr>
<tr><td>Creators</td><td>{esc(', '.join(creators))}</td></tr>
<tr><td>Licence</td><td><a href="{esc(license_)}">{esc(license_)}</a></td></tr>
<tr><td>Created / modified</td><td>{esc(created)} / {esc(modified)}</td></tr>
{f'<tr><td>Context</td><td>{esc(context)}</td></tr>' if context else ''}
{f'<tr><td>Location (WKT)</td><td><code>{esc(wkt)}</code></td></tr>' if wkt else ''}
{f'<tr><td>Temporal span</td><td>{esc(temporal_label)}</td></tr>' if temporal_label else ''}
<tr><td>Distributions</td><td>{len(dists)} files, {humanize_bytes(total_bytes)} total ({role_summary})</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>Sample distribution path</th><th>Role</th><th>Bytes</th></tr></thead>
<tbody>{sample_rows}</tbody>
</table>
{more_note}
<p class="note">Full record: <a href="{esc(record['doi'])}">{esc(record['doi'])}</a> —
as harvested by fdo-squirrel-registry: <a href="{esc(record['harvested_from'])}">source file</a></p>
</section>
"""


def vocabularies_section() -> str:
    all_prefixes: dict[str, str] = {}
    for key in ("example_software", "example_3d"):
        for p, uri in declared_prefixes(key):
            all_prefixes.setdefault(p, uri)
    rows = "".join(
        f"<tr><td><code>{esc(p)}</code></td><td><code>{esc(uri)}</code></td></tr>"
        for p, uri in sorted(all_prefixes.items())
    )
    return f"""<p class="note">The prefixes below are the <code>@prefix</code> lines actually present
in the two worked examples above, as harvested — not the crosswalk's declared target namespaces
(compare with the crosswalk table above). Notably, the crosswalk config declares
<code>fdo: https://w3id.org/fdo#</code>, but every record fdo-squirrel has actually written —
both worked examples here and fdo-squirrel-registry's own namespace table — uses
<code>fdo: https://w3id.org/fdo-squirrel/</code> instead. This looks like the crosswalk
config drifting from the generator (see PRIMER.md Teil D); worth confirming with
fdo-squirrel directly.</p>
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
below is built at render time from files copied out of fdo-squirrel and
fdo-squirrel-registry (see the provenance table at the end); it is not
hand-maintained prose and can go stale exactly when those repositories do —
run <code>python main.py fetch</code> to refresh, then <code>python main.py</code>
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
<h2>Worked examples</h2>
<p>Two real, harvested <code>fdo-metadata.ttl</code> instances from
<a href="{esc(SOURCE_REPO.rsplit('/', 1)[0] + '/fdo-squirrel-registry')}">fdo-squirrel-registry</a>,
one per FDO class currently represented there (no AnalysisFDO instance exists
yet). Unlike fdo-squirrel's own demo instance, these are single-class and
SHACL-gate-passed.</p>
{worked_example_section('example_software')}
{worked_example_section('example_3d')}
</section>

<section>
<h2>Vocabularies actually used</h2>
{vocabularies_section()}
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
