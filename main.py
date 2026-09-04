#!/usr/bin/env python3
"""fdo-squirrel-spec orchestrator.

    python main.py                     render docs/index.md from data/raw/
    python main.py --list              print steps and exit
    python main.py --only render       one step
    python main.py --dry-run           print the plan, run nothing
    python main.py --strict            warnings become errors (this is what CI runs)
    python main.py fetch               refresh data/raw/ from fdo-squirrel (pinned tag)
                                        and fdo-squirrel-registry (main, worked examples)
                                        (network; never part of the default run)
"""

from __future__ import annotations

import argparse
import importlib
import io
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "py"))

# Default pipeline, in order. Each entry: (name, module, function).
# "fetch" is deliberately not in here — see module docstring and PRIMER.md A3.
STEPS = [
    ("render", "step_render", "run"),
]


def run_step(name: str, module_name: str, func_name: str, strict: bool) -> tuple[bool, float, str]:
    t0 = time.time()
    buf = io.StringIO()
    ok = True
    try:
        with redirect_stdout(buf):
            mod = importlib.import_module(module_name)
            getattr(mod, func_name)()
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
        ok = False
        buf.write(f"ERROR in {name}: {exc}\n")
    elapsed = time.time() - t0
    output = buf.getvalue()
    for line in output.splitlines():
        print(f"[{name}] {line}")
    if strict and "WARNING" in output:
        ok = False
    return ok, elapsed, output


def select_steps(args) -> list[tuple[str, str, str]]:
    names = [s[0] for s in STEPS]
    if args.only:
        return [s for s in STEPS if s[0] == args.only]
    start = 0
    end = len(STEPS)
    if args.from_step:
        start = names.index(args.from_step)
    if args.skip:
        return [s for i, s in enumerate(STEPS) if i >= start and i < end and s[0] != args.skip]
    return STEPS[start:end]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("verb", nargs="?", choices=["fetch"], help="run a one-off verb instead of the pipeline")
    parser.add_argument("--list", action="store_true", help="print steps and exit")
    parser.add_argument("--only", metavar="STEP")
    parser.add_argument("--from", dest="from_step", metavar="STEP")
    parser.add_argument("--skip", metavar="STEP")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.verb == "fetch":
        importlib.import_module("step_fetch").run()
        return 0

    if args.list:
        for name, module_name, _ in STEPS:
            print(f"{name}  ({module_name})")
        return 0

    plan = select_steps(args)
    if args.dry_run:
        print("Plan:")
        for name, module_name, _ in plan:
            print(f"  {name}  ({module_name})")
        return 0

    results = []
    all_ok = True
    for name, module_name, func_name in plan:
        ok, elapsed, _ = run_step(name, module_name, func_name, args.strict)
        results.append((name, ok, elapsed))
        all_ok = all_ok and ok

    total = sum(r[2] for r in results) or 1e-9
    print("\nTiming:")
    for name, ok, elapsed in results:
        status = "ok" if ok else "FAILED"
        share = 100 * elapsed / total
        print(f"  {name:<10} {elapsed:6.2f}s  {share:5.1f}%  {status}")

    report_lines = [f"{name}: {'ok' if ok else 'FAILED'} ({elapsed:.2f}s)" for name, ok, elapsed in results]
    (ROOT / "dist").mkdir(parents=True, exist_ok=True)
    (ROOT / "dist" / "pipeline_report.txt").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8", newline="\n"
    )

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
