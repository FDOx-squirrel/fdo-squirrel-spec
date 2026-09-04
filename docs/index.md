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
      "url": "https://github.com/FDOx-squirrel",
      "list": "",
      "patentUri": ""
    },
    "editors": [
      {
        "name": "Florian Thiery",
        "company": "LEIZA / Research Squirrel Engineers",
        "url": "https://github.com/FDOx-squirrel"
      }
    ],
    "bibliography": {}
  }
---

<section id="abstract">
<p>This document specifies <dfn>MD.cff</dfn>, the metadata format read by
<a href="https://github.com/FDOx-squirrel/fdo-squirrel">fdo-squirrel</a> to turn a data package into a
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
<h2>Worked examples</h2>
<p>Two real, harvested <code>fdo-metadata.ttl</code> instances from
<a href="https://github.com/FDOx-squirrel/fdo-squirrel-registry">fdo-squirrel-registry</a>,
one per FDO class currently represented there (no AnalysisFDO instance exists
yet). Unlike fdo-squirrel's own demo instance, these are single-class and
SHACL-gate-passed.</p>

<section>
<h3>fdo:SoftwareFDO — Ogham 3D EpiDoc Extractor</h3>
<p class="note"><strong>As harvested, this record is invalid Turtle:</strong>
it uses the prefix(es) <code>crmdig, crm</code> without ever declaring them — a defect in the
fdo-squirrel version that produced it (fixed in later versions, see PRIMER.md A1). The file
on disk in this repository under <code>data/raw/examples/</code> is the unmodified harvested
original; the missing <code>@prefix</code> line(s) were added only in memory, the same way
fdo-squirrel-registry's own repair layer does it, to render this section.</p>
<p>LOD Extractor for TEI/EpiDoc Files from the Ogham in 3D Project</p>
<table>
<tbody>
<tr><td>Version</td><td>1.1</td></tr>
<tr><td>Creators</td><td>Thiery, Florian, Homburg, Timo</td></tr>
<tr><td>Licence</td><td><a href="https://spdx.org/licenses/MIT.html">https://spdx.org/licenses/MIT.html</a></td></tr>
<tr><td>Created / modified</td><td>2019-08-24 / 2024-09-24</td></tr>
<tr><td>Context</td><td>Ogham Stones in the Wild and in Museums in Ireland bearing Ogham inscriptions.</td></tr>
<tr><td>Location (WKT)</td><td><code>&lt;http://www.opengis.net/def/crs/EPSG/0/4326&gt; POINT(-8.0 53.0)</code></td></tr>
<tr><td>Temporal span</td><td>Ogham stone inscriptions (ca. 4th–7th century CE)</td></tr>
<tr><td>Distributions</td><td>242 files, 50.2 MB total (documentation: 2, script: 27, software: 213)</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>Sample distribution path</th><th>Role</th><th>Bytes</th></tr></thead>
<tbody><tr><td><code>.github/workflows/main.yml</code></td><td>software</td><td>879</td></tr><tr><td><code>.gitignore</code></td><td>software</td><td>9</td></tr><tr><td><code>ciic/bibliog.csv</code></td><td>software</td><td>64526</td></tr></tbody>
</table>
<p class="note">239 further distribution(s) omitted here for readability — see the full record for the complete list.</p>
<p class="note">Full record: <a href="https://doi.org/10.5281/zenodo.18369125">https://doi.org/10.5281/zenodo.18369125</a> —
as harvested by fdo-squirrel-registry: <a href="https://github.com/FDOx-squirrel/fdo-squirrel-registry/blob/main/data/raw/fdo/18369126/fdo-metadata.ttl">source file</a></p>
</section>


<section>
<h3>fdo:3DDataFDO — CO074-148----</h3>

<p>Ogham Stone CO074-148---- located in the UCC Stone Corridor (3 further description value(s) in this record, a data quality matter for fdo-squirrel-registry, not shown here)</p>
<table>
<tbody>
<tr><td>Version</td><td>1.0</td></tr>
<tr><td>Creators</td><td>Distel, Anne-Karoline, Thiery, Florian</td></tr>
<tr><td>Licence</td><td><a href="https://spdx.org/licenses/CC-BY-NC-SA-4.0.html">https://spdx.org/licenses/CC-BY-NC-SA-4.0.html</a></td></tr>
<tr><td>Created / modified</td><td>2024-06-05 / 2026-02-21</td></tr>
<tr><td>Context</td><td>Ogham Stones in the Wild and in Museums in Ireland bearing Ogham inscriptions.</td></tr>
<tr><td>Location (WKT)</td><td><code>&lt;http://www.opengis.net/def/crs/EPSG/0/4326&gt; POINT(-8.4924208 51.8937150)</code></td></tr>
<tr><td>Temporal span</td><td>Ogham stone inscriptions (ca. 4th–7th century CE)</td></tr>
<tr><td>Distributions</td><td>11 files, 283.7 MB total (data: 2, documentation: 3, metadata: 2, model: 4)</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>Sample distribution path</th><th>Role</th><th>Bytes</th></tr></thead>
<tbody><tr><td><code>CITATION.cff</code></td><td>metadata</td><td>326</td></tr><tr><td><code>CO074-148----.glb</code></td><td>model</td><td>126317064</td></tr><tr><td><code>CO074-148----.jpg</code></td><td>documentation</td><td>1311939</td></tr></tbody>
</table>
<p class="note">8 further distribution(s) omitted here for readability — see the full record for the complete list.</p>
<p class="note">Full record: <a href="https://doi.org/10.5281/zenodo.18724635">https://doi.org/10.5281/zenodo.18724635</a> —
as harvested by fdo-squirrel-registry: <a href="https://github.com/FDOx-squirrel/fdo-squirrel-registry/blob/main/data/raw/fdo/18744133/fdo-metadata.ttl">source file</a></p>
</section>

</section>

<section>
<h2>Vocabularies actually used</h2>
<p class="note">The prefixes below are the <code>@prefix</code> lines actually present
in the two worked examples above, as harvested — not the crosswalk's declared target namespaces
(compare with the crosswalk table above). Notably, the crosswalk config declares
<code>fdo: https://w3id.org/fdo#</code>, but every record fdo-squirrel has actually written —
both worked examples here and fdo-squirrel-registry's own namespace table — uses
<code>fdo: https://w3id.org/fdo-squirrel/</code> instead. This looks like the crosswalk
config drifting from the generator (see PRIMER.md Teil D); worth confirming with
fdo-squirrel directly.</p>
<table><thead><tr><th>Prefix</th><th>Namespace</th></tr></thead>
<tbody><tr><td><code>cff</code></td><td><code>https://citation-file-format.github.io/terms/</code></td></tr><tr><td><code>codemeta</code></td><td><code>https://codemeta.github.io/terms/</code></td></tr><tr><td><code>crm</code></td><td><code>http://www.cidoc-crm.org/cidoc-crm/</code></td></tr><tr><td><code>crmdig</code></td><td><code>http://www.ics.forth.gr/isl/CRMdig/</code></td></tr><tr><td><code>dcat</code></td><td><code>http://www.w3.org/ns/dcat#</code></td></tr><tr><td><code>dct</code></td><td><code>http://purl.org/dc/terms/</code></td></tr><tr><td><code>fdo</code></td><td><code>https://w3id.org/fdo-squirrel/</code></td></tr><tr><td><code>foaf</code></td><td><code>http://xmlns.com/foaf/0.1/</code></td></tr><tr><td><code>geosparql</code></td><td><code>http://www.opengis.net/ont/geosparql#</code></td></tr><tr><td><code>owl</code></td><td><code>http://www.w3.org/2002/07/owl#</code></td></tr><tr><td><code>rdf</code></td><td><code>http://www.w3.org/1999/02/22-rdf-syntax-ns#</code></td></tr><tr><td><code>rdfs</code></td><td><code>http://www.w3.org/2000/01/rdf-schema#</code></td></tr><tr><td><code>schema</code></td><td><code>https://schema.org/</code></td></tr><tr><td><code>sf</code></td><td><code>http://www.opengis.net/ont/sf#</code></td></tr><tr><td><code>wd</code></td><td><code>http://www.wikidata.org/entity/</code></td></tr><tr><td><code>wdt</code></td><td><code>http://www.wikidata.org/prop/direct/</code></td></tr><tr><td><code>xsd</code></td><td><code>http://www.w3.org/2001/XMLSchema#</code></td></tr></tbody></table>
</section>

<section id="conformance">
<p>This document has no independent conformance requirements: an MD.cff file
conforms if and only if it validates against the JSON Schema shipped in
<code>data/raw/MD.cff-schema.yaml</code> in this repository.</p>
</section>

<section class="appendix">
<h2>Provenance</h2>
<p>Built 2026-09-04 from these files (sha256, first 12 hex digits):</p>
<table><thead><tr><th>Source</th><th>Fingerprint</th></tr></thead>
<tbody><tr><td><code>schema</code></td><td><code>5f762f7408bf</code></td></tr><tr><td><code>crosswalk</code></td><td><code>542b30bae4fd</code></td></tr><tr><td><code>classification</code></td><td><code>561fc9def59c</code></td></tr><tr><td><code>package_source</code></td><td><code>19c867a6ac1d</code></td></tr><tr><td><code>example_software</code></td><td><code>a54ab63289fc</code></td></tr><tr><td><code>example_3d</code></td><td><code>e27114ffc2ce</code></td></tr></tbody></table>
</section>
