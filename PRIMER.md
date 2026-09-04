# PRIMER — fdo-squirrel-spec

Arbeitsplan für dieses Repo. Wird bei jedem Chat zu diesem Repo mit
hochgeladen und am Ende aktualisiert zurückgegeben. Teil A gilt immer und
wird nicht neu diskutiert, Teil B/C sind die Schritte, Teil D die offenen
Punkte.

## Teil A — Immer gültig

### A1 Ausgangslage

| Repo | Rolle |
|---|---|
| `FDOx-squirrel/fdo-squirrel` | Quelle der Wahrheit: liest ein FDO-Paket (ZIP), schreibt `fdo-metadata.ttl`. Enthält Schema, Crosswalk, Klassifikationsregeln. |
| `FDOx-squirrel/fdo-squirrel-registry` | zweite Quelle (seit S2): harvestet echte `fdo-metadata.ttl`-Instanzen von Zenodo; liefert die beiden Beispielinstanzen für dieses Repo. |
| `FDOx-squirrel/fdo-squirrel-md-generator` | eigenes, separates Repo (MD.cff/CFF-Generator) — nicht zu verwechseln mit diesem hier. |
| `FDOx-squirrel/fdo-squirrel-spec` (dieses Repo) | reine Dokumentation: rendert eine ReSpec-Seite aus Kopien der obigen Quelldateien. Publiziert selbst kein neues RDF. |

**Befunde (geprüft 2026-09-03):**

- `fdo-squirrel` enthält die vier für die Spec relevanten Quellen:
  `schemas/md_cff/MD.cff-schema.yaml` (JSON Schema draft 2020-12, `$id
  https://w3id.org/n4o/fdo/md-cff/schema/0.1`, `md_cff_version` const
  `"0.1"`, `fdo_type` enum `fdo:SoftwareFDO` / `fdo:AnalysisFDO` /
  `fdo:3DDataFDO`), `schemas/md_cff/crosswalk_md_cff_to_rdf.yaml`
  (regelbasierter Crosswalk nach DCAT/DCT, GeoSPARQL, CodeMeta, FDO — Präfix
  `fdo: https://w3id.org/fdo#`), `fdo/classification_rules.yaml`
  (Heuristiken: Dateiendung/Name/Pfad → Rolle, je FDO-Klasse), sowie
  `ingest/package_source.py`.
- **ZIP-Struktur ist nicht fix.** `package_source.py` sucht `MD.cff` und
  `CITATION.cff` per Kandidatenliste (`DEFAULT_MD_MEMBER_CANDIDATES`,
  `DEFAULT_CFF_MEMBER_CANDIDATES`): erst exakter Pfad, dann exakter
  Dateiname, dann eindeutiges `endswith`. Mehrdeutigkeit ist ein Fehler,
  keine Bestenauswahl. Quelle kann auch eine lose Datei oder eine URL sein.
- `fdo/fdo-metadata.ttl` (Demo-Instanz) **mischt Software- und
  3D-Metadaten** und taugt laut Befund aus einem früheren Chat
  ("FDO registry mit DCAT und SPARQL aufbauen", 2026-09-03) nicht als
  Referenzbeispiel. Hier deshalb nur zur Präfix-/Vokabular-Extraktion
  verwendet, nicht als vorzeigbare Beispielinstanz.
- `transmute-industries/respec-github-pages` baut auf **Jekyll + Ruby +
  `bundle`** und einer Liquid-Layout-Datei (`docs/_layouts/respec.html`)
  plus einem Versionsordner-Beispiel (`docs/v0.1.2/`, `docs/v1/index.json`).
  **Korrektur 2026-09-03 (derselbe Tag):** der ursprüngliche Schluss "das
  ist zu schwer, also verwerfen" war falsch — GitHub Pages baut Jekyll
  serverseitig bei jedem Push; Ruby/`bundle` wird nur für eine lokale
  Live-Vorschau gebraucht, nie für den Betrieb. Die Infra bleibt deshalb
  unverändert aus dem Template, nur `docs/index.md` (Inhalt) und
  `docs/_config.yml` (Titel/Beschreibung/URL) sind projektspezifisch.
  `docs/v0.1.2/` und `docs/v1/index.json` sind unverändert gelassene
  Platzhalter-Beispiele des Templates, nicht für dieses Projekt befüllt.
- `primer-repo`-Skill referenziert `assets/PRIMER.template.md`,
  `main_template.py`, `repo_utils_template.py`, `gitignore` — im
  Environment nicht vorhanden (nur `SKILL.md`). Hier direkt nach der
  Beschreibung im `SKILL.md` nachgebaut, nicht aus den Assets kopiert.

**Befunde (geprüft 2026-09-04, S2/S3):**

- **`fdo-squirrel` ist umgezogen:** die Org heißt jetzt `FDOx-squirrel`, nicht
  mehr `Research-Squirrel-Engineers` (die alte Org-URL liefert weiterhin
  `200`, ist aber GitHubs Auto-Weiterleitungsseite, keine echte Org mehr).
  Alle Referenzen in `README.md`, `py/fdo_squirrel_spec_utils.py` und
  `py/step_render.py` (RESPEC_CONFIG `group`/`editors`) auf `FDOx-squirrel`
  korrigiert.
- **`fdo-squirrel` taggt jetzt Releases:** `v0.1`, `v0.1.1`, `v0.2`, `v0.3`,
  `v0.3.1` existieren (per `git ls-remote --tags`, kein API-Rate-Limit).
  `main` (Commit `504b7af5`) ist bereits weiter als `v0.3.1` (Commit
  `9e35c344`): der Crosswalk bekommt dort einen `identifiers`-Feld-Mapping
  (Handler `typed_identifier`) und stellt den bbox-Handler von
  `dcat:bbox`/`literal` auf `geosparql:hasBoundingBox`/`bbox_envelope` um
  (WKT-`ENVELOPE(...)`-Konvertierung); `package_source.py` bekommt ein
  `package_local_path`-Feld (Tempfile-Schreiben beim ZIP-Download). Keine
  dieser Änderungen ist in `v0.3.1` enthalten — S3 pinnt bewusst auf die
  letzte *stabile* Version, nicht auf die neuesten unveröffentlichten
  Features (s. Teil D).
- **Crosswalk-Namespace-Mismatch:** `crosswalk_md_cff_to_rdf.yaml` deklariert
  `fdo: https://w3id.org/fdo#`, aber jede tatsächlich erzeugte Instanz — beide
  Beispielinstanzen hier wie auch `fdo-squirrel-registry`s eigene
  `PREFIXES`-Tabelle (`registry_utils.py`) — verwendet
  `fdo: https://w3id.org/fdo-squirrel/`. Sieht nach einer veralteten Angabe
  in der Crosswalk-Konfiguration aus, nicht nach einem Fehler in den
  Instanzen (s. Teil D).
- **3 von 7 bei `fdo-squirrel-registry` geharvesteten Records sind ungültiges
  Turtle:** sie schreiben `crmdig:D1, crm:E73` in die Typliste, ohne die
  Prefixe zu deklarieren — darunter beide bisher einzigen SoftwareFDO-Records
  (`18369126`, `18369157`). Die 4 neueren 3DDataFDO-Records sind sauber.
  `fdo-squirrel-registry`s eigenes `py/repair.py` datiert den Fix im
  Generator auf Jan–Feb 2026 und nennt es einen der "undokumentierten Fixes"
  aus `fdo-squirrel`s Commit-Historie (s. `fdo-squirrel`-PRIMER, Abschnitt zu
  den vier Fixes). Da Zenodo-Records unveränderlich sind, bleibt das
  dauerhaft so. Auf Flos Hinweis ("in einem der anderen family-repos haben
  wir die gefixt") die Reparaturregeln aus
  `fdo-squirrel-registry/py/repair.py` nach `py/example_repair.py` kopiert
  (nicht importiert) statt selbst neu erfunden — inkl. der zweiten,
  hier noch nicht ausgelösten Regel (unescaped quotes), weil "kopierter Code
  bringt seine Prüfungen mit" (A3).

### A2 Zielbild

```
fdo-squirrel (Tag v0.3.1)                fdo-squirrel-spec (dieses Repo)
  MD.cff-schema.yaml            ──┐
  crosswalk_md_cff_to_rdf.yaml  ──┼─ fetch ──▶ data/raw/ ── render ──▶ docs/index.md
  classification_rules.yaml     ──┤  (Netz)      (Snapshot)  (offline)   (Frontmatter + ReSpec-Body)
  ingest/package_source.py      ──┘                 │
                                                     │
fdo-squirrel-registry (main)                        │
  data/raw/fdo/18369126/fdo-metadata.ttl ─┐          │
  data/raw/fdo/18744133/fdo-metadata.ttl ─┼─ fetch ──▶ data/raw/examples/
                                          ┘  (Netz)      (Snapshot, ggf. defekt)
                                                                          │
                                                                GitHub Pages baut Jekyll
                                                                serverseitig ── docs/index.html
```

Eigenschaften, die das fertige Ding hat:

1. `docs/` bleibt die unveränderte `respec-github-pages`-Template-Infra
   (Jekyll-Layouts, Gemfile, CSS) — GitHub Pages baut sie bei jedem Push
   serverseitig, kein lokales Ruby/`bundle` für den Betrieb nötig.
2. Jede Tabelle in `docs/index.md` ist nachweisbar aus einer
   `data/raw/`-Datei generiert (Provenance-Tabelle am Seitenende mit
   sha256-Fingerprints), nicht von Hand abgeschrieben.
3. `python main.py fetch` zieht die Quelldateien frisch aus `fdo-squirrel`
   (Tag-gepinnt) und `fdo-squirrel-registry` (ungepinnt, `main`);
   `python main.py` baut `docs/index.md` danach offline und
   deterministisch (zweimal laufen lassen → `git status` bleibt leer, bis
   auf die Laufzeit in `dist/pipeline_report.txt`).
4. Es wird kein eigenes RDF publiziert — reine Dokumentation, A6 entfällt
   deshalb für dieses Repo.
5. Eine der beiden Beispielinstanzen ist als harvestet ungültiges Turtle;
   `py/example_repair.py` repariert nur in Erinnerung (nie auf der Platte)
   und die Seite sagt das offen, statt es zu verschweigen.

### A3 Querschnittsregeln

- Rohdaten liegen unverändert in `data/raw/`, read-only. Generiert wird
  ausschließlich nach `docs/` (die Spec-Seite) und `dist/`
  (Pipeline-Report).
- Reuse heißt kopieren, nicht referenzieren: `data/raw/` ist ein Snapshot,
  kein Live-Fetch bei jedem Build. Deshalb der eigene `fetch`-Schritt.
- Kein `datetime.now()` im Output. `RELEASE` in
  `py/fdo_squirrel_spec_utils.py` ist die einzige Stelle, an der ein Datum
  im generierten Output erscheinen darf.
- Zweimal laufen lassen, `git status` muss danach leer sein.
- Netzwerk ist auf den `fetch`-Schritt beschränkt; `render` läuft rein
  gegen `data/raw/`.
- `PRIMER.md` ist Deutsch, alles andere (Code, README, Kommentare) ist
  britisches Englisch.
- Windows ist die Referenzplattform: `cmd`-Befehle einzeilig.
- Kommunikation informell ("du").

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Repo-Name und Org | `fdo-squirrel-spec` unter `FDOx-squirrel` | 2026-09-03 |
| Quellen für `data/raw/` | `MD.cff-schema.yaml`, `crosswalk_md_cff_to_rdf.yaml`, `classification_rules.yaml`, `fdo-metadata.ttl` (nur für Präfixe, s. Befund), `package_source.py` | 2026-09-03 |
| ZIP-Struktur-Doku | abgeleitet aus `package_source.py` (Kandidatenlisten per `ast`, kein `exec`) + Prosa in README/PRIMER | 2026-09-03 |
| Template/Tooling für die Spec-Seite | `transmute-industries/respec-github-pages` (Jekyll), **unverändert** übernommen. Zwischenzeitlich als "zu schwer" verworfen zugunsten einer statischen `docs/index.html`, das war ein Fehlschluss: GitHub Pages baut Jekyll serverseitig, lokales Ruby/`bundle` ist nur für Live-Vorschau nötig, nicht für den Betrieb. `docs/index.md` (Frontmatter + ReSpec-Body) ersetzt die vorherige `docs/index.html`. | 2026-09-03, korrigiert denselben Tag |
| `specStatus` | `"unofficial"` (kein echter W3C-Prozess) | 2026-09-03, Vorschlag |
| Upstream-Ref für `fetch` (fdo-squirrel) | ~~`main`-Branch, ungepinnt~~ **S3 erledigt:** gepinnt auf Tag `v0.3.1`, da `fdo-squirrel` jetzt Releases taggt | 2026-09-03 Vorschlag, 2026-09-04 umgesetzt |
| Beispielinstanz für S2: Quelle | Live-Fetch aus `fdo-squirrel-registry` (zweite Quelle, `main`-Branch, ungepinnt — soll aktuell bleiben), nicht Referenz und nicht von Hand kuratiert | 2026-09-04 |
| Beispielinstanz für S2: Klassen | beide vorhandenen: `fdo:SoftwareFDO` (Record `18369126` / DOI `zenodo.18369125`) und `fdo:3DDataFDO` (Record `18744133` / DOI `zenodo.18724635`); `AnalysisFDO` noch nicht verfügbar bei der Registry | 2026-09-04 |
| `fdo/fdo-metadata.ttl` (Demo-Instanz) | nicht mehr gefetcht — Zweck (nur Präfix-Extraktion) jetzt durch die beiden echten Beispielinstanzen erfüllt | 2026-09-04 |
| Reparatur ungültigen harvesteten Turtles | `py/example_repair.py`, kopiert aus `fdo-squirrel-registry/py/repair.py` (Flo: "in einem der anderen family-repos haben wir die gefixt, das nachnutzen"). Repariert nur in Erinnerung beim Rendern, `data/raw/` bleibt der unveränderte Original-Fetch | 2026-09-04 |

### A5 Was in welchem Chat hochgeladen wird

Für Folgechats an diesem Repo: `PRIMER.md` plus Repo-Bundle, ohne
generierte Dateien erneut mitzuschleppen (die entstehen aus `main.py`
sowieso neu):

```cmd
cd /d C:\git
robocopy fdo-squirrel-spec bundle\fdo-squirrel-spec /E /XD .git .venv __pycache__ /XF *.pyc
powershell -NoProfile -Command "Compress-Archive -Path 'bundle\fdo-squirrel-spec' -DestinationPath 'fdo-squirrel-spec_bundle.zip' -Force"
```

Robocopy meldet Exitcode 1 bei Erfolg. Nicht hochladen: `.venv/`, `.git/`,
`config.local.json` (existiert hier nicht, aber falls später einer dazukommt).

### A6 IRI-Landkarte

Entfällt — dieses Repo publiziert kein eigenes RDF, es dokumentiert nur
Vokabulare, die anderswo (`fdo-squirrel`) definiert sind.

## Teil B — Schritte

| Schritt | Inhalt | Status |
|---|---|---|
| S1 | Skelett: Repo-Layout, `main.py`, `data/raw/`-Snapshot, `docs/index.md` erstmalig gerendert | **fertig (2026-09-03)** |
| S2 | Feinschliff Inhalt: zwei echte Beispielinstanzen (SoftwareFDO + 3DDataFDO) aus `fdo-squirrel-registry`, inkl. Reparatur-Layer für eine ungültige | **fertig (2026-09-04)** |
| S3 | `fetch` für `fdo-squirrel` auf stabilen Tag pinnen statt `main` | **fertig (2026-09-04)** |
| S4 | `owl-time`-artige Diagramme zur Package-Struktur (aus dem ursprünglichen S2 ausgelagert, s. Teil D) | offen |

## Teil C — Die Schritte im Detail

### S1 — Skelett

**Ziel:** Ein lauffähiges Repo, das aus einem `data/raw/`-Snapshot
deterministisch eine einzelne ReSpec-Seite baut.

**Uploads für diesen Schritt:** keine (Neuanlage) — Repo wird per
"Use this template"-Knopf von `transmute-industries/respec-github-pages`
angelegt, dessen Jekyll-Inhalt bleibt unverändert stehen (siehe A4), nur
`docs/index.md` und `docs/_config.yml` werden mit diesem Lieferumfang
überschrieben. Lieferung als normales Repo-ZIP zum direkten Entpacken in
das leere neue Repo, nicht als Patch (es gibt kein bestehendes Repo, gegen
das gepatcht werden könnte).

**Substanz:** `main.py`, `py/step_fetch.py`, `py/step_render.py`,
`py/fdo_squirrel_spec_utils.py`, `data/raw/*` (Snapshot, Commit `b7b6e58`
von `fdo-squirrel`), `requirements.txt`, `.gitignore`, `LICENSE`,
`CITATION.cff`, `README.md`.

**Abnahme:** `python main.py` läuft ohne Fehler, schreibt `docs/index.md`
und `dist/pipeline_report.txt`; ein zweiter Lauf ändert `git status` nicht
außer bei absichtlichen Quelländerungen.

**Erledigt 2026-09-03:** Im Sandkasten gegen eine leere Repo-Kopie
verifiziert (siehe `PATCH-README.md`, Abschnitt "Verified here").

### S2 — Echte Beispielinstanzen

**Ziel:** Die alte, kaputte Demo-Instanz (`fdo-squirrel`s
`fdo/fdo-metadata.ttl`, mischt SoftwareFDO- und 3DDataFDO-Felder) durch zwei
echte, validierte Beispielinstanzen ersetzen — eine pro verfügbarer FDO-Klasse
— und im Vorbeigehen sichtbar machen, wenn eine davon als harvestet
tatsächlich ungültiges Turtle ist.

**Uploads für diesen Schritt:** `PRIMER.md` + Repo-Bundle (s. A5).

**Substanz:**
- `py/fdo_squirrel_spec_utils.py`: `UPSTREAM_SOURCES` (zwei Quellen statt
  einer), `RAW_FILES` daraus abgeleitet, `EXAMPLE_RECORDS`,
  `EXAMPLE_PREFIXES` (kopiert aus `fdo-squirrel-registry/py/registry_utils.py`
  `PREFIXES`).
- `py/example_repair.py`: kopiert aus
  `fdo-squirrel-registry/py/repair.py` (beide Regeln: `missing_prefixes`,
  `unescaped_quotes`), repariert nur in Erinnerung.
- `py/step_fetch.py`: läuft jetzt über `UPSTREAM_SOURCES`, zwei Repos mit
  je eigenem Ref.
- `py/step_render.py`: `load_example()` (rdflib-Parse mit Reparatur-Fallback),
  `worked_example_section()` (kompakte, aus dem Graph extrahierte Übersicht
  statt Rohdump — bei 254 bzw. 11 Distributions wäre ein Volldump der falsche
  Detailgrad), `vocabularies_section()` jetzt aus den beiden echten Instanzen
  statt aus der Demo-Datei, inkl. Hinweis auf den `fdo:`-Namespace-Mismatch.
- `requirements.txt`: `rdflib>=7.0` neu (Begründung im Kommentar: eine der
  beiden Instanzen ist ungültiges Turtle, das verdient einen echten Parser
  plus eine deklarierte Reparatur, keinen Regex-Workaround).
- `README.md`, `CITATION.cff` (Version `0.2.0`), `main.py`-Docstring
  entsprechend nachgezogen; alle `Research-Squirrel-Engineers`-Referenzen auf
  `FDOx-squirrel` korrigiert (s. A1-Befund).

**Abnahme:** `python main.py fetch && python main.py` läuft fehlerfrei;
`docs/index.md` enthält für beide FDO-Klassen eine Worked-examples-Sektion
mit Quellenlink und, bei der SoftwareFDO-Instanz, den Reparaturhinweis;
zweiter Lauf lässt `git status` bis auf die Laufzeit in
`dist/pipeline_report.txt` leer — mit `PYTHONHASHSEED` 0/1/2/42 gegengeprüft
(gleicher sha256 von `docs/index.md` bei allen vier).

**Erledigt 2026-09-04:** Wie oben; die drei neuen Befunde (Org-Umzug,
main-vs-v0.3.1-Drift, Namespace-Mismatch, kaputtes Turtle bei 3/7
Registry-Records) sind in A1 festgehalten, die Entscheidungen in A4.

### S3 — Upstream-Ref pinnen

**Ziel:** `fetch` für `fdo-squirrel` von `main` auf einen stabilen Tag
umstellen, sobald einer existiert (A4, ursprünglich Vorschlag).

**Substanz:** `UPSTREAM_REF = "v0.3.1"` in
`py/fdo_squirrel_spec_utils.py`, `fdo-squirrel-registry` bewusst weiter auf
`main` (soll aktuell bleiben, taggt selbst nicht).

**Abnahme:** `python main.py fetch` zieht sichtbar von `.../v0.3.1/...`
(Log-Zeile), nicht `.../main/...`, für alle vier `fdo-squirrel`-Dateien.

**Erledigt 2026-09-04:** `git ls-remote --tags` zeigt `v0.1` … `v0.3.1`;
`main` (Commit `504b7af5`) ist neuer als `v0.3.1` (Commit `9e35c344`) und
enthält bereits ungetaggte Änderungen (Crosswalk-`identifiers`-Handler,
`geosparql:hasBoundingBox` statt `dcat:bbox`, `package_local_path`), die
dieser Fetch bewusst noch nicht zeigt, weil S3 explizit auf die letzte
*stabile* Version pinnt (s. A1-Befund, offener Punkt in Teil D für den
nächsten Tag).

## Teil D — Offene Punkte

- **S4** (neu, aus dem ursprünglichen S2 ausgelagert): `owl-time`-artige
  Diagramme zur Package-Struktur — eigener Schritt, damit dieser hier fokussiert
  bleibt.
- **Neuer Tag für S3:** `main` bei `fdo-squirrel` ist bereits weiter als
  `v0.3.1` (Crosswalk-`identifiers`-Handler, `geosparql:hasBoundingBox` statt
  `dcat:bbox`, `package_local_path`). Sobald ein neuer Tag das enthält, `fetch`
  erneut laufen lassen und `UPSTREAM_REF` bumpen — reiner Re-Fetch, kein neuer
  Beschluss nötig.
- **Crosswalk-Namespace-Mismatch:** `crosswalk_md_cff_to_rdf.yaml` deklariert
  `fdo: https://w3id.org/fdo#`, real erzeugte Instanzen nutzen
  `https://w3id.org/fdo-squirrel/`. Sollte das bei `fdo-squirrel` gemeldet
  werden, oder ist die Crosswalk-Deklaration einfach veraltet und wird bei
  Gelegenheit dort korrigiert? Betrifft nur die Doku hier, nicht diesen Code.
- **3 von 7 `fdo-squirrel-registry`-Records mit ungültigem Turtle:** dauerhaft
  so (Zenodo ist unveränderlich). Für dieses Repo durch `example_repair.py`
  gelöst; falls die Beispielinstanzen später gewechselt werden (z. B. sobald
  eine `AnalysisFDO`-Instanz existiert), erneut prüfen, ob der neue Record
  dieselben Reparaturregeln braucht oder eine neue.
- ORCID in `CITATION.cff` ist noch ein Platzhalter.
