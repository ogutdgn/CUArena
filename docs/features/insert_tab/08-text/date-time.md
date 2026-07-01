# Date & Time — Insert > Text

## What real Word does
Insert > Text > **Date & Time** opens the **Date and Time** dialog: pick a format from **Available formats** (date-only / time-only / combined), choose a **Language**, optionally a **Calendar type** (Gregorian/Hijri/Lunar/Saka/Um-al-Qura for some languages), tick **Update automatically** (insert a live DATE/TIME field vs static text), and **Set As Default**. Keys: Alt+Shift+D (DATE field), Alt+Shift+T (TIME field). The same dialog is shared by header/footer editing.

OOXML: Update-automatically OFF → a literal `w:r/w:t` with the date text. ON → a field: simple `w:fldSimple w:instr='DATE \@ "MMMM d, yyyy"'` (or TIME), or complex `w:fldChar begin / w:instrText 'DATE \@ …' / separate / result / end`. Calendar switches append to the instruction (`\h` Hijri, `\s` Saka).

## Current clone state
**working** — The dialog picks a format (`insert-features.js:186-196`) → `WC.PM.xeDateTime(fmt, {auto, text})` (`bridge/insert-exotica.ts:121-140`). When **Update automatically** is on (or no opts), it inserts a real `DATE \@ "fmt"` field via `insertField` → `d.fields.insert({instruction, mode:'raw'})` (updates on F9/open). When off (RB-050 fix), it inserts the formatted date as **static text** via `editor.chain().insertContent(text)`. So both the field and the static-text branches are real. Gaps: the format list is 6 fixed entries (vs Word's locale-driven list), no **Language** dropdown, no **Calendar type**, no **Set As Default**.

## Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** Both output paths already exist and round-trip — the static-text branch is plain `insertContent`, and the field branch rides the fork's real field engine (`field-references/fld-preprocessors/build-block-field-node.js` synthesizes `fldChar begin/separate/end` + `instrText` from the raw `DATE \@ …` instruction; `extensions/field-update/` resolves it on F9). Everything missing is **UI/data over the existing `xeDateTime`**: a richer locale-driven format list, a Language dropdown (the `\@` picture is just a string), a Set-As-Default persisted preference, and calendar `\h`/`\s` switches appended to the instruction. None of that touches a node type or a converter handler.

## Required structures to build it
- **PM node/extension:** reuse the field nodes / `fieldAnnotation` (DATE field) + plain text run (static).
- **Converter handler (super-converter):** exists — the field exporter writes `w:fldSimple`/`w:fldChar+instrText`; F9 update is `extensions/field-update/`.
- **OOXML target:** `w:fldSimple w:instr='DATE \@ "…"'` (auto) or `w:r/w:t` literal (static); calendar switches `\h`/`\s` appended.
- **Bridge verb(s):** `WC.PM.xeDateTime(fmt, {auto, text})` — already exists; extend opts with `{language, calendar}` to append the right `\@` picture/switches, and a `setAsDefault` preference read at dialog open.
- **Fork edit?** none.
- **Rough size:** S (format list + language + set-as-default) • **Dependencies:** rides the existing field engine.

## Open questions for our discussion
- **Format list fidelity:** generate the locale-driven Available-formats list (per chosen Language) like Word, or keep a broader fixed set? True locale formats need a date-format catalog.
- Add the **Language** dropdown + **Calendar type** (Hijri/Saka) switches, or English/Gregorian only for v1?
- **Set As Default** — persist the chosen format (and wire Alt+Shift+D / Alt+Shift+T to it)? Where do we store the preference?
- Worth matching Word's exact default highlighted format and Alt+Shift+D/T keybindings now?

## Decision
**TBD — to be decided together.**
