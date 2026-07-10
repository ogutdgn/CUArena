"""Step 4 signal 1 — PRODUCT-PURPOSE verdicts (authored, auditable).

Every verdict follows the mandated form (04-priority.md):
    product is X (identity) + this does Y (measured) -> therefore VERDICT
where X = the app identity measured in step 0 ("a desktop word processor for creating,
formatting and editing text documents") and Y = the node's measured what_it_does.
Verdicts: indispensable | important | useful | peripheral.

Writes priority/signals/product_purpose.json and FAILS LOUDLY if any scored (non-boundary)
sub-feature lacks a verdict — silence is not a score.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
X = "a desktop word processor whose core job is creating, formatting and editing text documents"

# id -> (verdict, Y — what it does, grounded in the measured rubric)
V = {
    # ---- Clipboard ----
    "subfeature:paste": ("indispensable", "inserts clipboard content at the cursor — the "
        "primary way content enters a document besides typing"),
    "subfeature:cut": ("important", "removes the selection to the clipboard — half of the "
        "move-content operation"),
    "subfeature:copy": ("indispensable", "duplicates the selection to the clipboard — "
        "content reuse is core to document work"),
    "subfeature:format-painter": ("useful", "copies formatting for reapplication — a "
        "convenience over re-applying formats manually"),
    "subfeature:office-clipboard": ("peripheral", "shows the last 24 clipboard items — the "
        "core job needs only the live clipboard"),
    # ---- Font ----
    "subfeature:font": ("indispensable", "chooses the typeface — formatting text is the "
        "core job and typeface is its first lever"),
    "subfeature:font-size": ("indispensable", "sets the character size — inseparable from "
        "formatted text"),
    "subfeature:font-size-increase": ("useful", "steps the size up — a variation of "
        "setting font size"),
    "subfeature:font-size-decrease": ("useful", "steps the size down — a variation of "
        "setting font size"),
    "subfeature:change-case": ("useful", "rewrites capitalization — a convenience over "
        "retyping"),
    "subfeature:clear-formatting": ("useful", "strips all formatting — a reset lever, not "
        "a creative one"),
    "subfeature:bold": ("indispensable", "toggles bold emphasis — the most-used character "
        "format in the product's own telemetry"),
    "subfeature:italic": ("important", "toggles italic emphasis — everyday emphasis, "
        "second to bold"),
    "subfeature:underline-gallery": ("important", "toggles underline (+styles/colors) — "
        "the third everyday emphasis"),
    "subfeature:strikethrough": ("useful", "strikes text through — edit-markup styling for "
        "specific tasks"),
    "subfeature:subscript": ("useful", "lowers text below the baseline — required for "
        "formulas/chemistry but absent from most documents"),
    "subfeature:superscript": ("useful", "raises text above the baseline — ordinals and "
        "footnote marks; task-specific"),
    "subfeature:text-effects": ("peripheral", "applies decorative visual effects — the core "
        "job is fine without decoration"),
    "subfeature:text-highlight-color-picker": ("important", "paints a highlighter color "
        "behind text — everyday review/emphasis tool"),
    "subfeature:font-color-picker": ("important", "sets text color — routine formatting, "
        "just below the emphasis trio"),
    "subfeature:font-dialog": ("important", "opens the consolidated character-formatting "
        "surface incl. defaults and advanced spacing — the deep end of a core capability"),
    # ---- Paragraph ----
    "subfeature:bullets-gallery": ("important", "starts/toggles bulleted lists — lists are "
        "core document structure"),
    "subfeature:numbering-gallery": ("important", "starts/toggles numbered lists — core "
        "document structure"),
    "subfeature:multilevel-list": ("useful", "applies nested list schemes — structured "
        "documents only"),
    "subfeature:indent-decrease": ("important", "moves the indent toward the margin — "
        "everyday paragraph layout"),
    "subfeature:indent-increase": ("important", "moves the indent away from the margin — "
        "everyday paragraph layout"),
    "subfeature:sort": ("peripheral", "sorts paragraphs/table rows — occasional data "
        "housekeeping, not document creation"),
    "subfeature:paragraph-marks": ("useful", "shows hidden formatting marks — a diagnostic "
        "view toggle"),
    "subfeature:align-left": ("important", "aligns paragraphs to the left margin — one of "
        "the four core alignments"),
    "subfeature:align-center": ("important", "centers paragraphs — titles and headings "
        "depend on it"),
    "subfeature:align-right": ("useful", "right-aligns paragraphs — situational (dates, "
        "signatures)"),
    "subfeature:align-justify": ("useful", "justifies both margins — style-specific"),
    "subfeature:line-spacing": ("important", "sets line/paragraph spacing — readable "
        "layout is core"),
    "subfeature:shading-color-picker": ("useful", "fills paragraph background color — "
        "decoration/emphasis, situational"),
    "subfeature:borders-selection-gallery": ("useful", "applies paragraph borders — "
        "decoration, situational"),
    "subfeature:paragraph-dialog": ("important", "opens the consolidated paragraph-layout "
        "surface (indents, spacing, pagination) — the deep end of a core capability"),
    # ---- Styles ----
    "subfeature:quick-styles": ("important", "applies named styles from the gallery — the "
        "product's own mechanism for consistent formatting"),
    "subfeature:styles-pane": ("useful", "opens the full style-management pane — power-user "
        "surface over the same capability"),
    # ---- Editing ----
    "subfeature:find": ("important", "searches document text — navigation in any non-trivial "
        "document"),
    "subfeature:replace": ("important", "substitutes text document-wide — bulk editing "
        "depends on it"),
    "subfeature:select": ("useful", "select-all/objects/similar-formatting — conveniences "
        "over mouse selection"),
    # ---- boundary Home groups ----
    "subfeature:dictate": ("peripheral", "cloud speech-to-text — an input alternative, not "
        "the core job"),
    "subfeature:editor": ("useful", "cloud proofing suggestions — quality aid, the document "
        "can be written without it"),
    "subfeature:create-pdf": ("peripheral", "exports PDF via a third-party add-in — output "
        "conversion, not document creation"),
    "subfeature:office-addins": ("peripheral", "opens the add-in store — an extension "
        "gateway, not a document capability"),
    # ---- Pages ----
    "subfeature:cover-page-insert": ("useful", "inserts a preformatted first page — "
        "template convenience"),
    "subfeature:blank-page-insert": ("useful", "inserts an empty page — a page-flow "
        "convenience over two breaks"),
    "subfeature:page-break-insert": ("important", "ends the page at the cursor — the basic "
        "page-flow control every multi-page document uses"),
    # ---- Tables ----
    "subfeature:table-insert": ("indispensable", "creates row/column structure — tables are "
        "one of the product's core artifacts (identity: formatting documents)"),
    # ---- Illustrations ----
    "subfeature:insert-pictures": ("indispensable", "places images into the document — "
        "graphics in text is a core capability of the product"),
    "subfeature:shapes-insert": ("useful", "draws vector shapes — diagramming inside "
        "documents, task-specific"),
    "subfeature:icon-insert": ("peripheral", "inserts stock icon graphics — decoration from "
        "a cloud library"),
    "subfeature:insert-3d-models": ("peripheral", "embeds rotatable 3D models — showcase "
        "content far from the core job"),
    "subfeature:smart-art-insert": ("useful", "inserts diagram graphics (lists, processes, "
        "hierarchies) — common in business docs, not core"),
    "subfeature:chart-insert": ("useful", "embeds a data chart with a linked worksheet — "
        "reporting documents need it, most documents do not"),
    "subfeature:screenshot-insert": ("peripheral", "snapshots an open window into the doc — "
        "an acquisition convenience"),
    # ---- Media / Links / Comments ----
    "subfeature:online-videos-insert": ("peripheral", "embeds online video — the core job "
        "is print-shaped documents"),
    "subfeature:insert-link": ("important", "wraps the selection in a hyperlink — digital "
        "documents live on links"),
    "subfeature:bookmark-insert": ("peripheral", "names a location for jumps — plumbing for "
        "links/references, rarely touched directly"),
    "subfeature:cross-reference-insert": ("useful", "inserts live references to "
        "headings/figures — long structured documents only"),
    "subfeature:insert-new-comment": ("important", "anchors a review comment — collaboration "
        "is core to modern document work"),
    # ---- Header & Footer ----
    "subfeature:header-insert": ("important", "puts repeating content at every page top — "
        "standard in formal documents"),
    "subfeature:footer-insert": ("important", "puts repeating content at every page bottom — "
        "standard in formal documents"),
    "subfeature:page-number-insert": ("important", "numbers the pages — near-universal in "
        "multi-page documents"),
    # ---- Text ----
    "subfeature:text-box-insert": ("useful", "adds a floating text container — layout "
        "flexibility for callouts/covers"),
    "subfeature:quick-parts-insert": ("peripheral", "inserts reusable building blocks and "
        "fields — power-user machinery"),
    "subfeature:word-art-insert": ("peripheral", "inserts decorative display text — pure "
        "decoration"),
    "subfeature:drop-cap-insert": ("peripheral", "drops the first letter large — a rare "
        "typographic flourish"),
    "subfeature:signature-line-insert": ("peripheral", "inserts a signature placeholder — "
        "specific business workflows"),
    "subfeature:date-and-time-insert": ("peripheral", "inserts the date/time, optionally "
        "auto-updating — typing the date is the common path"),
    "subfeature:object-insert": ("peripheral", "embeds OLE objects/files — legacy compound "
        "documents"),
    # ---- Symbols ----
    "subfeature:equation-insert-gallery": ("useful", "inserts a math zone with its own "
        "editing tab — capability-defining for technical writers, absent elsewhere"),
    "subfeature:symbol-insert": ("useful", "inserts characters not on the keyboard — "
        "everyone occasionally (©, ±, é)"),
    # ---- eSignature ----
    "subfeature:esignature-fields": ("peripheral", "starts a cloud e-signature request — an "
        "external service workflow"),
}

# Contextual sub-feature verdicts are appended by ctx (imported so the two files stay in
# sync with the spec's node ids).
try:
    from ctx_spec import CTX_PRODUCT_VERDICTS
    V.update(CTX_PRODUCT_VERDICTS)
except ImportError:
    CTX_PRODUCT_VERDICTS = {}


def main():
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    scored = [s["id"] for s in subs if not s.get("boundary")]
    missing = [i for i in scored if i not in V]
    extra = [i for i in V if i not in {s["id"] for s in subs}]
    nodes = {nid: {"verdict": verdict,
                   "reasoning": f"product is {X} + this {y} -> therefore {verdict}"}
             for nid, (verdict, y) in V.items()}
    out = KB / "priority" / "signals"
    out.mkdir(parents=True, exist_ok=True)
    (out / "product_purpose.json").write_text(json.dumps({
        "method": "authored verdict per sub-feature in the mandated form; verdict scores "
                  "mapped in combine_priority.py; identity X measured in step 0, function Y "
                  "measured in steps 2-3",
        "identity": X,
        "nodes": nodes}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"verdicts": len(nodes), "missing": missing, "extra": extra},
                     indent=2))
    if missing:
        raise SystemExit(f"{len(missing)} scored sub-features lack verdicts")


if __name__ == "__main__":
    main()
