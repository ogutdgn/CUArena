"""Design + Layout tree spec (word-4tabs-v1) — the NEW ground this run adds on top of the
Home+Insert tree and the shared contextual object machinery.

Grounded in the measured skeleton (Step 2 crawl of ui:ribbon-design / ui:ribbon-layout) and
this run's dumps. Cohesion decided by the playbook-03 tests (recorded per feature). The Layout
'Arrange' group is NOT a new feature — it is the SHARED feature:object-arrange (defined in
ctx_spec, measured on the object-format contextual tabs); the Layout Arrange controls are added
as extra trigger paths / hosts for those same subs (measured with an object selected in the
step3 layout-arrange pass). run_step3_tree imports these.
"""

RD = ["ui:main-window", "ui:ribbon-design"]
RL = ["ui:main-window", "ui:ribbon-layout"]

# feature id -> (name, tab-path, what_it_does, affects, audience, cohesion)
DL_FEATURES = {
    "feature:document-formatting": ("Document Formatting", RD,
        "Set the document's overall visual theme in one place — theme colors, fonts and "
        "effects, the style set, and document-wide paragraph spacing — and save the result as "
        "the default.",
        "the whole document's theme and default formatting", "most", "capability"),
    "feature:page-background": ("Page Background", RD,
        "Decorate the page itself: a watermark behind the content, a page background color, and "
        "a border around the page.",
        "the page's background decoration and border", "most", "catalog"),
    "feature:page-setup": ("Page Setup", RL,
        "Set up the printed page — margins, orientation, paper size, text columns, page/section "
        "breaks, line numbering and hyphenation.",
        "the page and section layout of the document", "everyone", "capability"),
    "feature:layout-paragraph": ("Paragraph (Layout)", RL,
        "Set the selected paragraph's precise left/right indentation and the spacing before and "
        "after it (the Layout tab's numeric Paragraph group).",
        "the selected paragraph's indentation and spacing", "most", "capability"),
}

# sub definitions: id -> dict(feature, name, does, affects, aud, els, opens, shortcut,
#                             source, boundary, tab)
# tab = RD or RL -> chooses the trigger-path base.
DL_SUBS = []
def _sub(id, feature, name, does, affects, aud, els, tab, opens=None, shortcut=None,
         source="measured"):
    DL_SUBS.append(dict(id=id, feature=feature, name=name, does=does, affects=affects,
                        aud=aud, els=els, opens=opens, shortcut=shortcut, source=source,
                        boundary=False, tab=tab))

# ---- Design > Document Formatting ----
_sub("subfeature:themes", "feature:document-formatting", "Themes",
     "Applies a document theme — a coordinated bundle of theme colors, fonts and effects — to "
     "the whole document from a gallery; also browse/reset/save themes.",
     "the document's whole theme (colors + fonts + effects)", "most",
     ["el:themes-gallery"], RD, opens="ui:themes-dropdown")
_sub("subfeature:style-set", "feature:document-formatting", "Style Set",
     "Applies a style set — a coordinated look for the built-in styles (Title, Headings, body) "
     "— from the in-ribbon gallery; also reset to the default or save a new set.",
     "the document's style set (how the built-in styles look)", "most",
     ["el:style-set-gallery"], RD, opens="ui:style-set-gallery")
_sub("subfeature:theme-colors", "feature:document-formatting", "Colors",
     "Changes the document theme's color scheme from a gallery (or customizes new theme "
     "colors).", "the document theme's colors", "most",
     ["el:theme-colors-gallery"], RD, opens="ui:theme-colors-dropdown")
_sub("subfeature:theme-fonts", "feature:document-formatting", "Fonts",
     "Changes the document theme's heading/body font pairing from a gallery (or customizes "
     "them).", "the document theme's fonts", "most",
     ["el:theme-fonts-gallery"], RD, opens="ui:theme-fonts-dropdown")
_sub("subfeature:paragraph-spacing-set", "feature:document-formatting", "Paragraph Spacing",
     "Applies a document-wide paragraph spacing preset (compact / open / double…) by adjusting "
     "the built-in styles' spacing.", "the whole document's paragraph spacing", "most",
     ["el:paragraph-spacing"], RD, opens="ui:paragraph-spacing-menu")
_sub("subfeature:theme-effects", "feature:document-formatting", "Effects",
     "Changes the document theme's graphic effects (shadow/reflection/line styling for shapes "
     "and charts) from a gallery.", "the document theme's graphic effects", "niche",
     ["el:theme-effects-gallery"], RD, opens="ui:theme-effects-dropdown")
_sub("subfeature:set-as-default", "feature:document-formatting", "Set as Default",
     "Sets the current theme/style-set/spacing formatting as the default for new documents "
     "based on this template.", "the template's default formatting", "niche",
     ["el:quick-styles-set-as-default"], RD, opens="ui:quick-styles-set-as-default-dialog")

# ---- Design > Page Background (catalog) ----
_sub("subfeature:watermark", "feature:page-background", "Watermark",
     "Stamps ghosted text or a picture (DRAFT, CONFIDENTIAL, a logo…) behind the document "
     "content on every page, from a gallery or a custom dialog.",
     "the page's watermark layer", "most",
     ["el:watermark-gallery"], RD, opens="ui:watermark-dropdown")
_sub("subfeature:page-color", "feature:page-background", "Page Color",
     "Fills the page background with a color, gradient, texture or picture (fill effects); "
     "chiefly for on-screen/web viewing.", "the page's background color/fill", "most",
     ["el:page-color-picker"], RD, opens="ui:page-color-menu")
_sub("subfeature:page-borders", "feature:page-background", "Page Borders",
     "Opens the Borders and Shading dialog on its Page Border tab to draw a decorative or "
     "line border around the whole page.", "the page's border frame", "most",
     ["el:page-border-and-shading-dialog"], RD, opens="ui:page-border-and-shading-dialog")

# ---- Layout > Page Setup ----
_sub("subfeature:page-margins", "feature:page-setup", "Margins",
     "Sets the page margins from presets (Normal/Narrow/Wide/Mirrored…) or a custom dialog; "
     "the top pick applies immediately.", "the page's margins", "everyone",
     ["el:page-margins-gallery"], RL, opens="ui:page-margins-dropdown")
_sub("subfeature:page-orientation", "feature:page-setup", "Orientation",
     "Switches the page between Portrait and Landscape.", "the page orientation", "everyone",
     ["el:page-orientation-gallery"], RL, opens="ui:page-orientation-dropdown")
_sub("subfeature:page-size", "feature:page-setup", "Size",
     "Chooses the paper size (Letter, A4, Legal…) from a gallery or a custom dialog.",
     "the page's paper size", "most",
     ["el:page-size-gallery"], RL, opens="ui:page-size-dropdown")
_sub("subfeature:page-columns", "feature:page-setup", "Columns",
     "Flows the document text into one or more newspaper-style columns (One/Two/Three/Left/"
     "Right or a custom dialog).", "the text's column layout", "most",
     ["el:table-columns-gallery"], RL, opens="ui:table-columns-dropdown")
_sub("subfeature:breaks", "feature:page-setup", "Breaks",
     "Inserts a page, column, text-wrapping or section break at the cursor from a menu — the "
     "control that starts a new page/column/section.",
     "the document's page/section flow", "most",
     ["el:breaks-gallery"], RL, opens="ui:breaks-menu")
_sub("subfeature:line-numbers", "feature:page-setup", "Line Numbers",
     "Adds line numbers in the margin (continuous, per-page, per-section) from a menu; used in "
     "legal and review documents.", "the document's line numbering", "niche",
     ["el:line-numbers-menu"], RL, opens="ui:line-numbers-menu")
_sub("subfeature:hyphenation", "feature:page-setup", "Hyphenation",
     "Controls automatic word hyphenation at line ends (None/Automatic/Manual + options).",
     "the document's hyphenation", "niche",
     ["el:hyphenation-menu"], RL, opens="ui:hyphenation-menu")
_sub("subfeature:page-setup-dialog", "feature:page-setup", "Page Setup dialog launcher",
     "Opens the Page Setup dialog — the consolidated surface for margins, paper, layout "
     "(section start, headers/footers distance, vertical alignment) and line numbers.",
     "opens the Page Setup dialog", "most",
     ["el:page-setup-dialog"], RL, opens="ui:page-setup-dialog")

# ---- Layout > Paragraph (numeric indent/spacing) ----
_sub("subfeature:indent-left", "feature:layout-paragraph", "Indent Left",
     "Sets the selected paragraph's left indent to a precise measurement (value field + "
     "More/Less steppers).", "the paragraph's left indent", "most",
     ["el:indent-left", "el:indent-left-more", "el:indent-left-less"], RL)
_sub("subfeature:indent-right", "feature:layout-paragraph", "Indent Right",
     "Sets the selected paragraph's right indent to a precise measurement (value field + "
     "More/Less steppers).", "the paragraph's right indent", "most",
     ["el:indent-right", "el:indent-right-more", "el:indent-right-less"], RL)
_sub("subfeature:spacing-before", "feature:layout-paragraph", "Spacing Before",
     "Sets the space above the selected paragraph in points (value field + More/Less "
     "steppers).", "the space before the paragraph", "most",
     ["el:spacing-before", "el:spacing-before-more", "el:spacing-before-less"], RL)
_sub("subfeature:spacing-after", "feature:layout-paragraph", "Spacing After",
     "Sets the space below the selected paragraph in points (value field + More/Less "
     "steppers).", "the space after the paragraph", "most",
     ["el:spacing-after", "el:spacing-after-more", "el:spacing-after-less"], RL)

# Existing nodes given an extra trigger path from a Design/Layout element:
# existing subfeature id -> [(tab_cid, el_id), ...]
DL_EXISTING_ELS = {
    # the Layout tab's Paragraph launcher opens the SAME Paragraph dialog as Home's launcher
    "subfeature:paragraph-dialog": [("ui:ribbon-layout", "el:paragraph-dialog")],
}

# Layout > Arrange controls -> the SHARED object-arrange subs (measured with an object
# selected in run_step3_layout_arrange). map: object-arrange sub id -> [el ids on Layout]
LAYOUT_ARRANGE_HOSTS = {
    "subfeature:object-position": ["el:picture-position-gallery"],
    "subfeature:object-text-wrap": ["el:text-wrap-gallery"],
    "subfeature:object-reorder": ["el:object-bring-forward", "el:object-bring-forward-dropdown",
                                  "el:object-send-backward", "el:object-send-backward-dropdown"],
    "subfeature:object-align": ["el:object-align-menu"],
    "subfeature:object-group": ["el:objects-group-menu"],
    "subfeature:object-rotate": ["el:object-rotate-gallery"],
    "subfeature:object-selection-pane": ["el:selection-pane"],
}

# ---- connections among Design/Layout nodes (measured/observed clusters) ----
DL_CLUSTERS = [
    (["subfeature:themes", "subfeature:theme-colors", "subfeature:theme-fonts",
      "subfeature:theme-effects", "subfeature:style-set", "subfeature:paragraph-spacing-set"],
     "affects-same", "shared-target",
     "all reshape the document's global theme/formatting layer"),
    (["subfeature:watermark", "subfeature:page-color", "subfeature:page-borders"],
     "co-location", "co-location", "the Page Background group — page-level decoration"),
    (["subfeature:page-margins", "subfeature:page-orientation", "subfeature:page-size",
      "subfeature:page-columns"], "affects-same", "shared-target",
     "all set the page's printable geometry (PageSetup)"),
    (["subfeature:indent-left", "subfeature:indent-right", "subfeature:spacing-before",
      "subfeature:spacing-after"], "affects-same", "shared-target",
     "all set the selected paragraph's indent/spacing metrics"),
]
# directed extras: (src, target, kind, source, why) — requires points AT the prerequisite
DL_EXTRA = [
    # theme layer feeds the style machinery
    ("subfeature:style-set", "subfeature:quick-styles", "affects-same", "observed",
     "a style set changes how the Quick Styles look"),
    ("subfeature:theme-colors", "subfeature:font-color-picker", "affects-same", "observed",
     "theme colors are the palette the Font Color picker offers"),
    ("subfeature:theme-fonts", "subfeature:font", "affects-same", "observed",
     "theme fonts are the (body/heading) fonts the Font box defaults to"),
    ("subfeature:paragraph-spacing-set", "subfeature:line-spacing", "affects-same", "observed",
     "both set paragraph spacing (document-wide preset vs per-paragraph)"),
    # Layout numeric indent vs Home step indent — same target
    ("subfeature:indent-left", "subfeature:indent-increase", "affects-same", "observed",
     "both change the paragraph's left indent (precise value vs one-step)"),
    ("subfeature:spacing-before", "subfeature:line-spacing", "affects-same", "observed",
     "both set paragraph spacing"),
    # Layout Breaks vs Insert Page Break — same page-flow target
    ("subfeature:breaks", "subfeature:page-break-insert", "affects-same", "observed",
     "the Breaks menu includes the page break the Insert tab also offers, plus section/column "
     "breaks"),
    # page borders shares the Borders and Shading dialog with paragraph borders
    ("subfeature:page-borders", "subfeature:borders-selection-gallery", "co-location",
     "observed", "both open the Borders and Shading dialog (different tab)"),
    # columns interact with section breaks (column layout applies per section)
    ("subfeature:page-columns", "subfeature:breaks", "affects-same", "observed",
     "multi-column layout is bounded by section breaks"),
]
# feature-level edges
DL_FEATURE_EDGES = [
    ("feature:document-formatting", "feature:styles", "affects-same", "observed",
     "the theme/style-set drives how the named styles render"),
    ("feature:page-setup", "feature:header-footer", "affects-same", "observed",
     "page setup (margins, section breaks) governs where headers/footers and page flow sit"),
    ("feature:layout-paragraph", "feature:paragraph", "affects-same", "observed",
     "the Layout Paragraph group is the numeric half of the same paragraph formatting"),
]

# product-purpose verdicts for Step 4: id -> (verdict, Y)
DL_PRODUCT_VERDICTS = {
    "subfeature:themes": ("useful", "applies a whole-document theme — a quick way to make a "
        "document look coordinated, but most users keep the default"),
    "subfeature:style-set": ("useful", "restyles the built-in styles — occasional polish"),
    "subfeature:theme-colors": ("useful", "changes the theme palette — occasional branding"),
    "subfeature:theme-fonts": ("useful", "changes the theme font pairing — occasional"),
    "subfeature:paragraph-spacing-set": ("useful", "applies a document-wide spacing preset — "
        "occasional layout choice"),
    "subfeature:theme-effects": ("peripheral", "changes theme graphic effects — rarely noticed "
        "unless the doc has many shapes/charts"),
    "subfeature:set-as-default": ("peripheral", "saves current formatting as the template "
        "default — a one-time power action"),
    "subfeature:watermark": ("useful", "stamps DRAFT/CONFIDENTIAL/logo behind the page — common "
        "in formal/business documents"),
    "subfeature:page-color": ("peripheral", "fills the page background color — mainly for "
        "on-screen/web docs; rarely printed"),
    "subfeature:page-borders": ("useful", "draws a border around the page — common on flyers, "
        "certificates and title pages"),
    "subfeature:page-margins": ("important", "sets page margins — a near-universal page-setup "
        "choice on real documents"),
    "subfeature:page-orientation": ("important", "portrait vs landscape — a fundamental page "
        "choice"),
    "subfeature:page-size": ("useful", "sets paper size — usually left at the default but "
        "essential when it must change (A4 vs Letter)"),
    "subfeature:page-columns": ("useful", "flows text into columns — newsletters/brochures, "
        "occasional"),
    "subfeature:breaks": ("important", "inserts page/section/column breaks — core to "
        "structuring any multi-page document"),
    "subfeature:line-numbers": ("peripheral", "adds margin line numbers — legal/review niche"),
    "subfeature:hyphenation": ("peripheral", "controls hyphenation — rarely touched by most "
        "users"),
    "subfeature:page-setup-dialog": ("useful", "the consolidated page-setup surface — power "
        "page setup"),
    "subfeature:indent-left": ("useful", "sets a precise left indent — common in formal "
        "layout, though the ruler/Increase Indent are more used"),
    "subfeature:indent-right": ("useful", "sets a precise right indent — occasional"),
    "subfeature:spacing-before": ("useful", "sets space before a paragraph — common spacing "
        "control"),
    "subfeature:spacing-after": ("useful", "sets space after a paragraph — common spacing "
        "control"),
}
