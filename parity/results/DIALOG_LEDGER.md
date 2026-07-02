# Dialog Ledger — clone dialog fields vs Word UIA dump (D2.2)

Word side = UIA field/tab dump (dump_dialog_uia.ps1); clone side = rendered dialog DOM
(dialog-fields-probe.js). Scope = locked-feature dialogs.

**Dialogs compared: 6** · **fields missing in clone: 58**

| Dialog | Status | fields matched | missing | extra | tabs missing |
|---|---|---|---|---|---|
| font | compared | 16 | **6** | 3 | advanced, font |
| paragraph | compared | 7 | **14** | 1 | indents and spacing, line and page breaks |
| findadv | compared | 0 | **18** | 3 | find, go to, replace |
| wordcount | compared | 1 | **6** | 0 | — |
| paste_special | compared | 0 | **10** | 0 | — |
| insert_table | compared | 2 | **4** | 0 | — |
| page_setup | clone-dialog-missing | — | — | — | — |

## font — missing fields (Word has, clone lacks)

- Underline color (ComboBox)
- Ligatures (ComboBox)
- Number spacing (ComboBox)
- Number forms (ComboBox)
- Stylistic sets (ComboBox)
- Use Contextual Alternates (CheckBox)

## paragraph — missing fields (Word has, clone lacks)

- Outline level (ComboBox)
- Collapsed by default (CheckBox)
- Special (ComboBox)
- By (Spinner)
- Mirror indents (CheckBox)
- Line spacing (ComboBox)
- Tabs... (Button)
- Widow/Orphan control (CheckBox)
- Keep with next (CheckBox)
- Keep lines together (CheckBox)
- Page break before (CheckBox)
- Suppress line numbers (CheckBox)
- Don't hyphenate (CheckBox)
- Tight wrap (ComboBox)

## findadv — missing fields (Word has, clone lacks)

- Find what (ComboBox)
- Replace with (ComboBox)
- Search (ComboBox)
- Match case (CheckBox)
- Find whole words only (CheckBox)
- Use wildcards (CheckBox)
- Sounds like (English) (CheckBox)
- Find all word forms (English) (CheckBox)
- Match prefix (CheckBox)
- Match suffix (CheckBox)
- Ignore punctuation characters (CheckBox)
- Ignore white-space characters (CheckBox)
- Format (Button)
- Special (Button)
- No Formatting (Button)
- Replace (Button)
- Replace All (Button)
- Find Next (Button)

## wordcount — missing fields (Word has, clone lacks)

- Pages (Text)
- Words (Text)
- Characters (no spaces) (Text)
- Characters (with spaces) (Text)
- Paragraphs (Text)
- Lines (Text)

## paste_special — missing fields (Word has, clone lacks)

- Paste (RadioButton)
- Paste link (RadioButton)
- As (List)
- Microsoft Word Document Object (ListItem)
- Formatted Text (RTF) (ListItem)
- Unformatted Text (ListItem)
- Picture (Enhanced Metafile) (ListItem)
- HTML Format (ListItem)
- Unformatted Unicode Text (ListItem)
- Display as icon (CheckBox)

## insert_table — missing fields (Word has, clone lacks)

- Fixed column width (RadioButton)
- AutoFit to contents (RadioButton)
- AutoFit to window (RadioButton)
- Remember dimensions for new tables (CheckBox)
