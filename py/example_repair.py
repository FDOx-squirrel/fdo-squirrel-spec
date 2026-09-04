"""Declared, minimal repairs applied to a harvested worked-example TTL before
it is parsed for rendering.

Copied (not imported - PRIMER A3, reuse means copying) from
fdo-squirrel-registry/py/repair.py as of 2026-09-04, where it exists because
three of the seven records fdo-squirrel-registry has harvested so far -
including both currently available SoftwareFDO instances - were written by a
version of fdo-squirrel that emitted `crmdig:D1, crm:E73` in the class list
without ever declaring either prefix. A Zenodo record is immutable, so no
upstream correction can reach them; fdo-squirrel-registry's own PRIMER dates
the fix in the generator to Jan-Feb 2026 and treats this as one of the
"undokumentierten Fixes" only visible in fdo-squirrel's commit history.

Two properties make a repair here an *encoding* fix rather than an invented
one, same as upstream:

  * It only fills in a binding the generator itself uses elsewhere (see
    EXAMPLE_PREFIXES in fdo_squirrel_spec_utils.py) - never a guess.
  * data/raw/examples/*.ttl on disk stays exactly what was fetched. Repair
    happens in memory in step_render.py; content_fingerprint() in the
    provenance table therefore always hashes the true harvested bytes, and
    the rendered page says plainly when a repair was needed.

A file needing more than the rules below is not suffering from a known,
evidenced defect; that is a reason to pick a different worked example, not to
extend this module.
"""

from __future__ import annotations

import re

# rdflib's complaint, e.g. 'Bad syntax (Prefix "crmdig:" not bound)'
_UNBOUND = re.compile(r'Prefix "([A-Za-z][\w.-]*):" not bound')


def missing_prefixes(text: str, error: Exception, known: dict[str, str]) -> tuple[str, str] | None:
    """Prepend an @prefix line for a prefix the file uses but never declares."""
    match = _UNBOUND.search(str(error))
    if not match:
        return None
    prefix = match.group(1)
    if prefix not in known:
        return None
    line = f"@prefix {prefix}: <{known[prefix]}> .\n"
    return line + text, f"missing-prefix:{prefix}"


# predicate, then a literal that runs to the end of the line and is closed by
# ; or . - the shape the generator writes one statement per line in. Not
# currently triggered by either chosen worked example, kept because it is the
# other half of the same evidenced repair layer upstream and costs nothing to
# carry along (PRIMER A3: copied code carries its checks with it).
_ONE_LINE_LITERAL = re.compile(r'^(\s*[\w.-]+:[^\s"]+\s+)"(.*)"(\s*[;.]\s*)$')


def unescaped_quotes(text: str, error: Exception, known: dict[str, str]) -> tuple[str, str] | None:
    """Escape `"` inside a literal that spans the rest of its line."""
    changed = False
    out = []
    for line in text.splitlines(keepends=True):
        match = _ONE_LINE_LITERAL.match(line.rstrip("\n"))
        if match:
            head, body, tail = match.groups()
            fixed = re.sub(r'(?<!\\)"', r'\\"', body)
            if fixed != body:
                line = f'{head}"{fixed}"{tail}\n'
                changed = True
        out.append(line)
    if not changed:
        return None
    return "".join(out), "unescaped-quote"


RULES = (missing_prefixes, unescaped_quotes)

# A file needing more than this many rounds is not suffering from the two
# known defects; guessing further is how a repair layer starts inventing
# content.
MAX_ROUNDS = 12


def repair(text: str, parse, known: dict[str, str]) -> tuple[str, list[str]]:
    """Apply rules until the text parses or no rule matches.

    `parse` is called with the text and must raise on invalid Turtle. Returns
    the (possibly unchanged) text and the list of repairs applied, in order.
    """
    applied: list[str] = []
    for _ in range(MAX_ROUNDS):
        try:
            parse(text)
            return text, applied
        except Exception as error:  # noqa: BLE001 - rdflib raises plain Exception
            for rule in RULES:
                result = rule(text, error, known)
                if result is not None:
                    text, label = result
                    applied.append(label)
                    break
            else:
                return text, applied  # no rule matched: give up
    return text, applied
