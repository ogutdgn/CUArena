#!/usr/bin/env python3
"""Download + recolour the Fluent icons the ribbon uses into resources/icons/.

Reads resources/ribbon-icons.txt (emitted by build_ribbon.py), pulls each
`<name>_24_regular.svg` from the @fluentui/svg-icons package via jsDelivr
(DECISIONS D-icons — MIT licensed), recolours the single-colour `#212121`
path fill to the ribbon's icon tint, and writes resources/icons/<name>.svg.

Word-style theming: the icon stays one constant colour; the button background
conveys hover/active/disabled (RibbonButton.qml). Re-theming = re-run with a
different --color (we own theming — Boundary A).

Run from apps/writer/:  python3 tools/fetch_icons.py [--color "#E6E6E6"]
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "resources" / "ribbon-icons.txt"
OUTDIR = ROOT / "resources" / "icons"
PKG = "1.1.328"  # pinned @fluentui/svg-icons version for reproducibility
URL = ("https://cdn.jsdelivr.net/npm/@fluentui/svg-icons@" + PKG +
       "/icons/{name}_24_regular.svg")

# Paths in this package carry no fill (inherit default black); a few icons
# specify a dark fill explicitly. So: (1) recolour explicit dark fills, and
# (2) set the inherited fill on the <svg> root for the fill-less paths.
DARK_FILL_RE = re.compile(r'fill="(#212121|#000000|black)"', re.IGNORECASE)
SVG_OPEN_RE = re.compile(r"<svg\b([^>]*)>")


def recolour(svg: str, color: str) -> str:
    svg = DARK_FILL_RE.sub(f'fill="{color}"', svg)

    def fix_root(m: "re.Match[str]") -> str:
        attrs = m.group(1)
        if 'fill="' in attrs:  # replace whatever the root declared
            attrs = re.sub(r'fill="[^"]*"', f'fill="{color}"', attrs, count=1)
        else:
            attrs = f' fill="{color}"' + attrs
        return f"<svg{attrs}>"

    return SVG_OPEN_RE.sub(fix_root, svg, count=1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--color", default="#E6E6E6", help="icon tint (hex)")
    ap.add_argument("--force", action="store_true", help="re-download existing")
    args = ap.parse_args()

    names = [n for n in LIST.read_text().split() if n]
    OUTDIR.mkdir(parents=True, exist_ok=True)

    ok, skipped, failed = 0, 0, []
    for name in names:
        dest = OUTDIR / f"{name}.svg"
        if dest.exists() and not args.force:
            # always re-apply colour so a tint change takes without --force
            dest.write_text(recolour(dest.read_text(), args.color))
            skipped += 1
            continue
        try:
            with urllib.request.urlopen(URL.format(name=name), timeout=20) as r:
                svg = r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            failed.append((name, str(e)))
            continue
        before = svg
        svg = recolour(svg, args.color)
        if svg == before:
            print(f"   (warn) no #212121 fill recoloured in {name}", file=sys.stderr)
        dest.write_text(svg)
        ok += 1

    print(f"icons: {ok} downloaded, {skipped} already present (recoloured), "
          f"{len(failed)} failed -> {OUTDIR.relative_to(ROOT)}", file=sys.stderr)
    for name, err in failed:
        print(f"   FAIL {name}: {err}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
