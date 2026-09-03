# PRIMER — fdo-squirrel-spec

Arbeitsplan für dieses Repo. Wird bei jedem Chat zu diesem Repo mit
hochgeladen und am Ende aktualisiert zurückgegeben. Teil A gilt immer und
wird nicht neu diskutiert, Teil B/C sind die Schritte, Teil D die offenen
Punkte.

## Teil A — Immer gültig

### A1 Ausgangslage

| Repo | Rolle |
|---|---|
| `Research-Squirrel-Engineers/fdo-squirrel` | Quelle der Wahrheit: liest ein FDO-Paket (ZIP), schreibt `fdo-metadata.ttl`. Enthält Schema, Crosswalk, Klassifikationsregeln. |
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

### A2 Zielbild

```
fdo-squirrel (Quelle)                    fdo-squirrel-spec (dieses Repo)
  MD.cff-schema.yaml            ──┐
  crosswalk_md_cff_to_rdf.yaml  ──┼─ fetch ──▶ data/raw/ ── render ──▶ docs/index.md
  classification_rules.yaml     ──┤  (Netz)      (Snapshot)  (offline)   (Frontmatter + ReSpec-Body)
  ingest/package_source.py      ──┘                                          │
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
3. `python main.py fetch` zieht die Quelldateien frisch aus `fdo-squirrel`;
   `python main.py` baut `docs/index.md` danach offline und
   deterministisch (zweimal laufen lassen → `git status` bleibt leer).
4. Es wird kein eigenes RDF publiziert — reine Dokumentation, A6 entfällt
   deshalb für dieses Repo.

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
| Upstream-Ref für `fetch` | `main`-Branch von `fdo-squirrel`, ungepinnt auf Commit-Ebene | 2026-09-03, Vorschlag |

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
| S1 | Skelett: Repo-Layout, `main.py`, `data/raw/`-Snapshot, `docs/index.md` erstmalig gerendert | **fertig (dieses ZIP)** |
| S2 | Feinschliff Inhalt: Beispielinstanz (validiertes, nicht das kaputte Demo-TTL), evtl. `owl-time`-artige Diagramme zur Package-Struktur | offen |
| S3 | `fetch` gegen echten Commit pinnen statt `main`, sobald ein stabiler Tag in `fdo-squirrel` existiert | offen |

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

## Teil D — Offene Punkte

- Beispielinstanz für S2: welches reale (nicht das kaputte Demo-)
  `fdo-metadata.ttl` als Vorzeigebeispiel? Aus der FDO-Registry
  (`fdo-squirrel-registry`) wäre eine Option, aber das ist ein anderes Repo
  mit eigenem Lebenszyklus — referenzieren oder eine eigene, kuratierte
  Minimalinstanz in `data/raw/` pflegen?
- `fetch` zieht aktuell vom `main`-Branch. Sobald `fdo-squirrel` Releases
  taggt, sollte hier auf einen Tag umgestellt werden (S3).
- ORCID in `CITATION.cff` ist noch ein Platzhalter.
