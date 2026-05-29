#!/usr/bin/env python3
"""
Build the CUA Word-dark color scheme by duplicating COLOR_SCHEME_LIBREOFFICE_DARK
inside officecfg/.../Office/UI.xcu, renaming to COLOR_SCHEME_CUA_WORD_DARK,
and setting explicit Word M365 dark palette values for the high-impact keys.

Idempotent: if CUA_WORD_DARK already exists, replaces it.
Vanilla scheme nodes (AUTOMATIC, LIGHT, DARK) are not modified.

Run from repo root.

After running:
- Build (`make` in WSL) to regenerate xcd registry.
- Restart soffice — Tools -> Options -> Appearance will show "CUA Word Dark"
  as the current scheme.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
UI_XCU = REPO_ROOT / "apps/ms-word/libreoffice-codebase/officecfg/registry/data/org/openoffice/Office/UI.xcu"

NEW_SCHEME = "COLOR_SCHEME_CUA_WORD_DARK"

# Word M365 dark palette mapped to ThemeColors keys.
# Only the high-impact "Group Application" + a few General keys are pinned.
# Other keys inherit from the duplicated DARK scheme (which is mostly nil ->
# system default) so we minimize visual surprise.
def hex_to_int(h):
    h = h.lstrip("#")
    return int(h, 16)

WORD_PALETTE = {
    # Group General — document chrome
    "DocColor":            hex_to_int("#FFFFFF"),  # paper stays white
    "AppBackground":       hex_to_int("#1F1F1F"),  # area behind doc
    "FontColor":           hex_to_int("#F0F0F0"),  # default UI text on dark

    # Group Application — VCL widget paint
    "WindowColor":         hex_to_int("#2B2B2B"),  # ribbon body, menu bg
    "WindowTextColor":     hex_to_int("#F0F0F0"),
    "BaseColor":           hex_to_int("#1F1F1F"),  # input/list bg
    "ButtonColor":         hex_to_int("#2B2B2B"),
    "ButtonTextColor":     hex_to_int("#F0F0F0"),
    "AccentColor":         hex_to_int("#2B5797"),  # Word classic blue
    "ActiveColor":         hex_to_int("#4A9EFF"),  # active tab / hover accent
    "DisabledColor":       hex_to_int("#3A3A3A"),
    "DisabledTextColor":   hex_to_int("#888888"),
    "ShadowColor":         hex_to_int("#1A1A1A"),
    "SeparatorColor":      hex_to_int("#3A3A3A"),
    "FaceColor":           hex_to_int("#2B2B2B"),
    "MenuColor":           hex_to_int("#2B2B2B"),
    "MenuTextColor":       hex_to_int("#F0F0F0"),
    "MenuBarColor":        hex_to_int("#2B2B2B"),
    "MenuBarTextColor":    hex_to_int("#F0F0F0"),
    "MenuBarHighlightColor":     hex_to_int("#2B5797"),
    "MenuBarHighlightTextColor": hex_to_int("#FFFFFF"),
    "MenuHighlightColor":        hex_to_int("#2B5797"),
    "MenuHighlightTextColor":    hex_to_int("#FFFFFF"),
    "MenuBorderColor":      hex_to_int("#1A1A1A"),
    "InactiveColor":        hex_to_int("#3A3A3A"),
    "InactiveTextColor":    hex_to_int("#888888"),
    "InactiveBorderColor":  hex_to_int("#3A3A3A"),

    # Writer-specific (high-visibility on the page)
    "WriterFieldShadings":     hex_to_int("#3A4A60"),  # subtle blue field hint
    "WriterHeaderFooterMark":  hex_to_int("#4A4A4A"),
    "WriterPageBreaks":        hex_to_int("#666666"),
    "WriterIdxShadings":       hex_to_int("#3A4A60"),
    "WriterSectionBoundaries": hex_to_int("#3A3A3A"),
}


def main():
    if not UI_XCU.exists():
        sys.exit(f"FATAL: not found: {UI_XCU}")

    src = UI_XCU.read_text(encoding="utf-8")

    # If we already added CUA_WORD_DARK, remove the old block first
    # (idempotent). Use the same shape we wrote it in: a top-level node
    # right after COLOR_SCHEME_LIBREOFFICE_DARK. We anchor on
    # COLOR_SCHEME_CUA_WORD_DARK and stop at the matching </node>\n
    # of THIS scheme (not deeper). Since scheme nodes always close with
    # exactly 6 spaces of indent ("      </node>"), use that anchor.
    re_existing = re.compile(
        r'      <node oor:name="' + NEW_SCHEME + r'" oor:op="replace">\n.*?\n      </node>\n',
        re.DOTALL,
    )
    if re_existing.search(src):
        print(f"  removing existing {NEW_SCHEME} block (idempotent)")
        src = re_existing.sub("", src)

    # 1. Flip CurrentColorScheme value
    cs_pat = re.compile(
        r'(<prop oor:name="CurrentColorScheme">\s*<value>)[^<]+(</value>\s*</prop>)'
    )
    if not cs_pat.search(src):
        sys.exit("FATAL: CurrentColorScheme prop not found")
    src, n = cs_pat.subn(r"\g<1>" + NEW_SCHEME + r"\g<2>", src, count=1)
    print(f"  CurrentColorScheme -> {NEW_SCHEME} (replaced {n})")

    # 2. Extract COLOR_SCHEME_LIBREOFFICE_DARK block
    dark_pat = re.compile(
        r'(\s*<node oor:name="COLOR_SCHEME_LIBREOFFICE_DARK" oor:op="replace">.*?\n      </node>\n)',
        re.DOTALL,
    )
    m = dark_pat.search(src)
    if not m:
        sys.exit("FATAL: COLOR_SCHEME_LIBREOFFICE_DARK block not found")
    dark_block = m.group(1)

    # 3. Duplicate: rename + apply Word palette overrides
    new_block = dark_block.replace(
        'oor:name="COLOR_SCHEME_LIBREOFFICE_DARK"',
        f'oor:name="{NEW_SCHEME}"',
        1,
    )
    # 3a. For each Word palette key, replace its Color prop's nil value
    # with the integer. Keys may have other props (e.g. IsVisible) before
    # the Color prop, so allow any content inside the node block until we
    # find the Color value.
    for key, color_int in WORD_PALETTE.items():
        node_pat = re.compile(
            r'(<node oor:name="' + re.escape(key) + r'">'
            r'(?:(?!</node>).)*?'
            r'<prop oor:name="Color">\s*<value)( xsi:nil="true"/>)',
            re.DOTALL,
        )
        new_block, replaced = node_pat.subn(
            r'\g<1>>' + str(color_int) + r'</value>',
            new_block,
            count=1,
        )
        if replaced == 0:
            print(f"  WARN: key not found in DARK scheme: {key}")

    # 4. Insert new block right after DARK block
    insert_pos = m.end()
    src = src[:insert_pos] + new_block + src[insert_pos:]

    UI_XCU.write_text(src, encoding="utf-8")
    print(f"  wrote: {UI_XCU}")
    print(f"  applied {len(WORD_PALETTE)} color overrides")


if __name__ == "__main__":
    main()
