"""Step 5 depth reconciliation, pass 2 — resolve the nested option-dialog OPENERS ("More Fill
Colors…", "3-D Options…", "More Gradients…", "More Layout Options…", …) to the SHARED surfaces
they open, which the transitive walk ALREADY captured elsewhere (the seen-set: one Colors dialog
/ one Format-Shape pane, reached from many "More…/…Options…" entry points). This turns an
R2.4/R5.4 gap into a measured `opens` edge without re-driving a surface already in the KB.

Standard Office openers map to standard surfaces:
  * "More * Colors…"                     -> the shared Colors dialog
  * "* Options…" (3-D/Glow/Shadow/Reflection/Bevel/Soft Edges/Rotation), "More Gradients…",
    "More Textures…", "More Lines…", "More Fill…"  -> the family's Format-<object> pane
  * "More Layout Options…"               -> the family's Layout dialog
  * "Text Effects…", "* Text * "         -> the family's Format Text Effects pane
  * "Picture…" / "Select Picture…"       -> an Insert Picture dialog (OS/boundary, already stubbed)
Family = the `ui:ribbon-<family>-…` prefix of the opener's container; Home/Insert openers use
the shared (non-family) captures. Openers with no captured target are printed for a live re-drive.
Idempotent.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB


def ell(l):
    s = (l or "").rstrip()
    return s.endswith(("...", "…")) and any(c.isalpha() for c in s)


def fam_of(cid):
    m = re.match(r"ui:ribbon-(table-design|table-layout|picture-format|graphics-format|"
                 r"shape-format|smart-art-design|smart-art-format|chart-design|chart-format|"
                 r"equation|header-footer)-", cid)
    return m.group(1) if m else None


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    containers = ui.containers

    explored = {cid: c for cid, c in containers.items() if c.explored}

    def find(pred):
        for cid, c in explored.items():
            if pred(cid, (c.label or "").lower()):
                return cid
        return None

    colors_dialog = find(lambda i, l: l == "colors" and containers[i].kind == "dialog")

    def format_pane(fam):
        # the family's fill/line/effects surface (Format Object/Picture/Shape pane)
        pri = [f"ui:ribbon-{fam}-object-format-pane",
               f"ui:ribbon-{fam}-picture-format-pane",
               f"ui:ribbon-{fam}-graphics-format-pane",
               f"ui:ribbon-{fam}-shape-format-pane"]
        for p in pri:
            if p in explored:
                return p
        return find(lambda i, l: fam and fam in i and "format" in l and containers[i].kind == "pane"
                    and "text" not in l and "selection" not in l and "alt" not in l)

    def text_pane(fam):
        return find(lambda i, l: fam and fam in i and containers[i].kind == "pane"
                    and ("text effect" in l or "word" in i))

    def layout_dialog(fam):
        c = f"ui:ribbon-{fam}-layout-options-dialog-size-dialog"
        if c in explored:
            return c
        return find(lambda i, l: fam and fam in i and l == "layout" and containers[i].kind == "dialog")

    picture_dialog = find(lambda i, l: l == "insert picture" and containers[i].kind == "dialog")

    def resolve(cid, lab):
        fam = fam_of(cid)
        low = lab.lower().rstrip(" .…").strip()
        if "color" in low and low.startswith("more"):
            return colors_dialog
        if low in ("picture", "select picture") or low.endswith("picture"):
            return picture_dialog
        if "layout option" in low:
            return layout_dialog(fam) or None
        if "text" in low and ("effect" in low or "fill" in low or "outline" in low):
            return text_pane(fam) or format_pane(fam)
        if (low.endswith("options") or low.startswith("more gradient")
                or low.startswith("more texture") or low.startswith("more line")
                or low.startswith("more fill") or "options" in low):
            return format_pane(fam)
        return None

    rewrites, residual = 0, []
    for cid, c in list(containers.items()):
        changed = False
        for e in c.children:
            lab = e.label or ""
            if not ell(lab) or not e.unexplored:
                continue
            low = lab.lower()
            if "office.com" in low:
                continue
            tgt = resolve(cid, lab)
            if tgt and tgt != cid and tgt in containers:
                e.unexplored = False
                e.opens = tgt
                e.state_notes = ((e.state_notes or "") +
                                 f"; opener resolved to the shared surface {tgt} (seen-set — "
                                 "one surface reached from many entry points)").strip("; ")
                rewrites += 1
                changed = True
            else:
                residual.append((cid, lab))
        if changed:
            writer.upsert_container(c)

    jrnl = common.get_journal(common.make_run_id() + "-reconcile-options")
    jrnl.append(common.journal_event(actor="stage5.reconcile", action="reconcile-options",
                target="nested-option-openers", outcome="ok",
                data={"resolved": rewrites, "colors_dialog": colors_dialog,
                      "residual": [f"{c}::{l}" for c, l in residual]}))
    print(json.dumps({"resolved_to_shared": rewrites, "colors_dialog": colors_dialog,
                      "residual_count": len(residual)}, indent=2))
    if residual:
        print("\nRESIDUAL (no captured target — need re-drive):")
        for c, l in residual:
            print(f"   {c} :: {l}")


if __name__ == "__main__":
    main()
