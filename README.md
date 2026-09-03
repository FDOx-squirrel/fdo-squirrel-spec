# fdo-squirrel-spec

Generated specification of **MD.cff**, the metadata format read by
[fdo-squirrel](https://github.com/Research-Squirrel-Engineers/fdo-squirrel)
to build FAIR Digital Objects: package (ZIP) structure, the MD.cff JSON
Schema, the crosswalk to RDF, and the file classification rules.

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
copied from `fdo-squirrel`, not hand-transcribed:

```
data/raw/*.yaml, *.ttl, package_source.py   (copied snapshot of fdo-squirrel)
        │
        ▼  python main.py            (render step, offline)
docs/index.md                         (Jekyll front matter + ReSpec body)
        │
        ▼  GitHub Pages (Jekyll build, server-side, no local step needed)
docs/index.html                       (published)
```

```
python main.py fetch     # refresh data/raw/ from fdo-squirrel (network)
python main.py           # rebuild docs/index.md from data/raw/ (offline)
python main.py --list    # show available steps
python main.py --dry-run # show the plan without running anything
```

Requires Python 3.9+ and `pip install -r requirements.txt`.

## Repository layout

| Path | Contents |
|---|---|
| `data/raw/` | Snapshot of the upstream schema/crosswalk/classification files |
| `py/step_fetch.py` | Refreshes `data/raw/` from `fdo-squirrel` (network) |
| `py/step_render.py` | Builds `docs/index.md` from `data/raw/` (offline) |
| `docs/` | respec-github-pages template (Jekyll), unmodified except `index.md` and `_config.yml` |
| `PRIMER.md` | Internal (German) working plan — decisions, findings, steps |

## License

MIT, see [LICENSE](LICENSE).
