# Import Sketch file

- **Category:** imports
- **One-line summary:** Import a `.sketch` file into Figma; layers / styles / artboards convert to Figma equivalents.

## Triggers
- File browser → **Import** → choose `.sketch` file.

## Preconditions
- Valid `.sketch` file.

## Inputs
- File picker.

## Behavior
1. Figma converts artboards → frames, symbols → components (per article `import-sketch-files`).
2. Some advanced Sketch features may not translate (gradients, plugins).
3. Imported file appears in current project.

## Outputs
- **Persistent state:** new file imported.

## UI feedback
- Progress indicator during import.

## Side effects
- N/A.

## Related UI schema entries
- `regions/floating-overlays.md` → file-browser-import

## Semantic event(s) candidate
- `import_sketch_file { source_file_name, new_file_id, conversion_summary, trigger }`

## Source articles
- `import-sketch-files`
- `import-files-to-the-file-browser`
- `guide-to-imports-in-figma-design`
- `copy-assets-between-design-tools`
- `start-designing-with-ui-kits`
- `get-started-with-apples-ui-kit`
