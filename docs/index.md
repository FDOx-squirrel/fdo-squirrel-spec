---
layout: respec
title: MD.cff — Metadata Format for FDO Squirrel
respec: >
  {
    "name": "fdo-squirrel-spec",
    "status": "unofficial",
    "latest": "https://fdox-squirrel.github.io/fdo-squirrel-spec/",
    "repository": "https://github.com/FDOx-squirrel/fdo-squirrel-spec",
    "issues": "https://github.com/FDOx-squirrel/fdo-squirrel-spec/issues",
    "group": {
      "name": "Research Squirrel Engineers",
      "url": "https://github.com/Research-Squirrel-Engineers",
      "list": "",
      "patentUri": ""
    },
    "editors": [
      {
        "name": "Florian Thiery",
        "company": "LEIZA / Research Squirrel Engineers",
        "url": "https://github.com/Research-Squirrel-Engineers"
      }
    ],
    "bibliography": {}
  }
---

<section id="abstract">
<p>This document specifies <dfn>MD.cff</dfn>, the metadata format read by
<a href="https://github.com/Research-Squirrel-Engineers/fdo-squirrel">fdo-squirrel</a> to turn a data package into a
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
<p>A package is a ZIP archive. There is no fixed internal layout — the loader
identifies the metadata files by matching candidate names against the archive
members, in this order: (1) an exact-path match if one was configured,
(2) an exact filename match against the candidate list, (3) an unambiguous
<code>endswith</code> match. More than one match at the same step is a hard
error rather than a guess.</p>
<table>
<thead><tr><th>Role</th><th>Candidate filenames</th></tr></thead>
<tbody>
<tr><td>MD.cff (FDO metadata)</td><td>MD.cff</td></tr>
<tr><td>CITATION.cff</td><td>CITATION.cff, citation.cff</td></tr>
</tbody>
</table>
<p class="note">Both files may also sit at the ZIP root as loose files instead
of inside an archive, and either may be supplied by URL (a remote ZIP is
downloaded and read the same way).</p>
</section>

<section>
<h2>MD.cff schema</h2>
<p>MD.cff version <code>0.1</code>.
Target FDO classes:</p>
<ul><li><code>fdo:SoftwareFDO</code></li><li><code>fdo:AnalysisFDO</code></li><li><code>fdo:3DDataFDO</code></li></ul>
<h3>Properties</h3>
<table><thead><tr><th>Property</th><th>Type</th><th>Required</th><th>Description</th></tr></thead><tbody><tr><td><code>md_cff_version</code></td><td>string</td><td>yes</td><td>MD.cff schema version (this spec).</td></tr><tr><td><code>fdo_type</code></td><td>string</td><td>yes</td><td>Target FDO class.</td></tr><tr><td><code>id</code></td><td>string</td><td>yes</td><td>Global identifier for the described resource (prefer DOI/ARK/Handle/URL).</td></tr><tr><td><code>title</code></td><td>string</td><td>yes</td><td></td></tr><tr><td><code>description</code></td><td>string</td><td>yes</td><td>Human-readable description of the described object.</td></tr><tr><td><code>version</code></td><td>string</td><td>no</td><td>Human-readable version of the described object (not schema version).</td></tr><tr><td><code>date_created</code></td><td>string</td><td>no</td><td>Creation date (ISO 8601, YYYY-MM-DD).</td></tr><tr><td><code>date_released</code></td><td>string</td><td>no</td><td>Release/publication date (ISO 8601, YYYY-MM-DD).</td></tr><tr><td><code>date_modified</code></td><td>array</td><td>no</td><td>Modification dates (ISO 8601, YYYY-MM-DD).</td></tr><tr><td><code>funding</code></td><td>array</td><td>no</td><td>Funding statements or references.</td></tr><tr><td><code>keywords</code></td><td>array</td><td>no</td><td>Keywords as {label,id?}. label is required; id is optional (URI recommended).</td></tr><tr><td><code>license</code></td><td>—</td><td>no</td><td>License as {label,id?}. label required; id optional (URI recommended, e.g., SPDX URL).</td></tr><tr><td><code>publishers</code></td><td>array</td><td>yes</td><td>Publishing agents as list of {label,id?}.</td></tr><tr><td><code>creators</code></td><td>array</td><td>no</td><td>Primary creators/authors (use {label,id?}).</td></tr><tr><td><code>contributors</code></td><td>array</td><td>no</td><td>Contributors (use {label,id?}).</td></tr><tr><td><code>identifiers</code></td><td>array</td><td>no</td><td>Additional identifiers (e.g., DOI, URL, GitHub, ORCID).</td></tr><tr><td><code>related_resources</code></td><td>array</td><td>no</td><td>Links to related objects (papers, datasets, repos, etc.).</td></tr><tr><td><code>distributions</code></td><td>array</td><td>no</td><td>Optional distributions (files, downloads).</td></tr><tr><td><code>spatial</code></td><td>—</td><td>no</td><td>Optional spatial extent (label/id plus geometry/bbox).</td></tr><tr><td><code>temporal</code></td><td>—</td><td>no</td><td>Optional temporal extent (label/id plus start/end).</td></tr><tr><td><code>heritage_object</code></td><td>—</td><td>no</td><td>Optional heritage-object specific metadata.</td></tr><tr><td><code>technique</code></td><td>—</td><td>no</td><td>Optional technique metadata (3D acquisition/processing and/or software specifics).</td></tr></tbody></table>
</section>

<section>
<h2>File classification rules</h2>
<p>Once a package is identified as belonging to an FDO class, each file inside
it is assigned a role by matching against ordered rules for that class.</p>
<table><thead><tr><th>FDO class</th><th>Match rule</th><th>Assigned role</th></tr></thead><tbody><tr><td><code>fdo:SoftwareFDO</code></td><td>extension: .py, .r, .js, .java</td><td>script</td></tr><tr><td><code>fdo:SoftwareFDO</code></td><td>filename: setup.py, pyproject.toml, requirements.txt</td><td>configuration</td></tr><tr><td><code>fdo:SoftwareFDO</code></td><td>extension: .exe, .jar, .bin</td><td>software</td></tr><tr><td><code>fdo:SoftwareFDO</code></td><td>filename_prefix: README; extension: .md, .rst, .txt</td><td>documentation</td></tr><tr><td><code>fdo:SoftwareFDO</code></td><td>filename: MD.cff, CITATION.cff</td><td>metadata</td></tr><tr><td><code>fdo:SoftwareFDO</code></td><td>path_prefix: tests/</td><td>auxiliary</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>extension: .ipynb</td><td>script</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>extension: .py, .r</td><td>script</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>extension: .csv, .tsv, .parquet, .json</td><td>data</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>path_prefix: results/</td><td>result</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>extension: .png, .jpg, .pdf</td><td>result</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>filename_prefix: README; extension: .md, .txt</td><td>documentation</td></tr><tr><td><code>fdo:AnalysisFDO</code></td><td>filename: MD.cff, CITATION.cff</td><td>metadata</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>extension: .obj, .ply, .stl, .glb, .gltf, .nxs, .nxz, .xyz, .pts, .ptx, .dae</td><td>model</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>extension: .jpg, .jpeg, .png, .tif, .tiff, .pdf, .csv, .xml, .json</td><td>documentation</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>extension: .las, .laz</td><td>data</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>path_prefix: textures/</td><td>auxiliary</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>filename_prefix: README; extension: .md, .txt</td><td>documentation</td></tr><tr><td><code>fdo:3DDataFDO</code></td><td>filename: MD.cff, CITATION.cff</td><td>metadata</td></tr></tbody></table>
</section>

<section>
<h2>Crosswalk to RDF</h2>
<p>MD.cff fields are lifted to RDF (DCAT/DCT, GeoSPARQL, CodeMeta, FDO) using
named handlers over the following namespaces:</p>
<table><thead><tr><th>Prefix</th><th>Namespace</th></tr></thead><tbody><tr><td><code>rdf</code></td><td><code>http://www.w3.org/1999/02/22-rdf-syntax-ns#</code></td></tr><tr><td><code>rdfs</code></td><td><code>http://www.w3.org/2000/01/rdf-schema#</code></td></tr><tr><td><code>dct</code></td><td><code>http://purl.org/dc/terms/</code></td></tr><tr><td><code>dcat</code></td><td><code>http://www.w3.org/ns/dcat#</code></td></tr><tr><td><code>schema</code></td><td><code>https://schema.org/</code></td></tr><tr><td><code>codemeta</code></td><td><code>https://codemeta.github.io/terms/</code></td></tr><tr><td><code>geosparql</code></td><td><code>http://www.opengis.net/ont/geosparql#</code></td></tr><tr><td><code>sf</code></td><td><code>http://www.opengis.net/ont/sf#</code></td></tr><tr><td><code>fdo</code></td><td><code>https://w3id.org/fdo#</code></td></tr></tbody></table>
<h3>Handlers</h3>
<ul><li><dfn>geosparql_geometry</dfn> — Create geometry node with CRS-prefixed WKT and sf:* type</li><li><dfn>temporal_node</dfn> — Create temporal node and attach start/end dates</li></ul>
</section>

<section>
<h2>Vocabularies in the example instance</h2>
<p class="note">The vocabularies below are the namespaces declared in
fdo-squirrel's demo instance. That instance is known to mix fields from more
than one FDO class and is <strong>not</strong> reproduced here as a worked
example for that reason — only the namespace list is derived from it.</p>
<table><thead><tr><th>Prefix</th><th>Namespace</th></tr></thead>
<tbody><tr><td><code>dcat</code></td><td><code>http://www.w3.org/ns/dcat#</code></td></tr><tr><td><code>dct</code></td><td><code>http://purl.org/dc/terms/</code></td></tr><tr><td><code>fdo</code></td><td><code>https://w3id.org/fdo-squirrel/</code></td></tr><tr><td><code>schema</code></td><td><code>https://schema.org/</code></td></tr><tr><td><code>xsd</code></td><td><code>http://www.w3.org/2001/XMLSchema#</code></td></tr></tbody></table>
</section>

<section id="conformance">
<p>This document has no independent conformance requirements: an MD.cff file
conforms if and only if it validates against the JSON Schema shipped in
<code>data/raw/MD.cff-schema.yaml</code> in this repository.</p>
</section>

<section class="appendix">
<h2>Provenance</h2>
<p>Built 2026-09-03 from these files (sha256, first 12 hex digits):</p>
<table><thead><tr><th>Source</th><th>Fingerprint</th></tr></thead>
<tbody><tr><td><code>schema</code></td><td><code>5f762f7408bf</code></td></tr><tr><td><code>crosswalk</code></td><td><code>177987905b81</code></td></tr><tr><td><code>classification</code></td><td><code>561fc9def59c</code></td></tr><tr><td><code>example_ttl</code></td><td><code>9ada967d3bf6</code></td></tr><tr><td><code>package_source</code></td><td><code>c16ac42a43fd</code></td></tr></tbody></table>
</section>
