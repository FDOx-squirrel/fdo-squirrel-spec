# fdo-squirrel-spec

Generated specification of **MD.cff**, the metadata format read by
[fdo-squirrel](https://github.com/FDOx-squirrel/fdo-squirrel)
to build FAIR Digital Objects: package (ZIP) structure, the MD.cff JSON
Schema, the crosswalk to RDF, and the file classification rules — plus two
real, harvested worked examples (one per FDO class available) sourced from
[fdo-squirrel-registry](https://github.com/FDOx-squirrel/fdo-squirrel-registry).

**[Read the spec](https://fdox-squirrel.github.io/fdo-squirrel-spec/)**

## How this repository works

`docs/` is the [respec-github-pages](https://github.com/transmute-industries/respec-github-pages)
template, unmodified: Jekyll layouts, Gemfile, and CSS as shipped. GitHub
Pages builds it automatically on push — no Ruby/Jekyll toolchain is required
locally unless you want a live preview (see the template's own README for
that, linked above).

The only project-specific pieces are `docs/index.md`'s content and
`docs/_config.yml`'s title/description/URL. `docs/index.md` is generated —
every table in it is derived from a file in `data/raw/`, a plain snapshot
copied from two upstream repositories, not hand-transcribed:

```
data/raw/*.yaml, package_source.py     (snapshot of fdo-squirrel, tag-pinned)
data/raw/examples/*.ttl                (snapshot of fdo-squirrel-registry, main)
        │
        ▼  python main.py            (render step, offline)
docs/index.md                         (Jekyll front matter + ReSpec body)
        │
        ▼  GitHub Pages (Jekyll build, server-side, no local step needed)
docs/index.html                       (published)
```

The two worked-example instances are real, SHACL-gate-passed records
harvested by fdo-squirrel-registry, one `SoftwareFDO` and one `3DDataFDO` —
not fdo-squirrel's own demo instance, which mixes fields from both classes.
One of the two is invalid Turtle as originally written (a missing `@prefix`,
fixed in later fdo-squirrel versions); `py/example_repair.py` repairs it in
memory for rendering only, never on disk, and the page says so.

```
python main.py fetch     # refresh data/raw/ from upstream (network)
python main.py           # rebuild docs/index.md from data/raw/ (offline)
python main.py --list    # show available steps
python main.py --dry-run # show the plan without running anything
```

Requires Python 3.9+ and `pip install -r requirements.txt`.

## Repository layout

| Path | Contents |
|---|---|
| `data/raw/` | Snapshot of the upstream schema/crosswalk/classification files |
| `data/raw/examples/` | Snapshot of two real worked-example FDO instances from `fdo-squirrel-registry` |
| `py/step_fetch.py` | Refreshes `data/raw/` from `fdo-squirrel` and `fdo-squirrel-registry` (network) |
| `py/step_render.py` | Builds `docs/index.md` from `data/raw/` (offline) |
| `py/example_repair.py` | Minimal, evidenced repairs for known-invalid harvested Turtle, applied in memory only |
| `docs/` | respec-github-pages template (Jekyll), unmodified except `index.md` and `_config.yml` |
| `PRIMER.md` | Internal (German) working plan — decisions, findings, steps |

## License

MIT, see [LICENSE](LICENSE).
