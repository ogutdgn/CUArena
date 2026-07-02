'use strict';
// Generates src/renderer/core/generated/table-style-defs.ts from the locked-build oracle
// captures (parity/oracle/table_style_defs.json — 113 real Word 16.0 table-style defs).
// CommonJS, like the sibling generators (scripts/gen.js, scripts/gen-icons.js).
//
// Regenerate: node scripts/gen-table-style-defs.js
//
// Section rule (gallery bucket, derived from the display name family):
//   name starts with 'Plain Table' or 'Table Grid', or === 'Table Normal' → 'plain'
//   name starts with 'Grid Table'                                          → 'grid'
//   name starts with 'List Table'                                          → 'list'
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SRC = path.join(ROOT, 'parity', 'oracle', 'table_style_defs.json');
const OUT = path.join(ROOT, 'src', 'renderer', 'core', 'generated', 'table-style-defs.ts');

/** Derive the gallery section from the Word display name family. */
function sectionFor(name) {
  const n = String(name || '');
  if (n.startsWith('Plain Table') || n.startsWith('Table Grid') || n === 'Table Normal') return 'plain';
  if (n.startsWith('Grid Table')) return 'grid';
  if (n.startsWith('List Table')) return 'list';
  // Should not happen for the locked catalog (all 113 match); bucket defensively as 'plain'.
  return 'plain';
}

const oracle = JSON.parse(fs.readFileSync(SRC, 'utf8'));
const styles = oracle.styles || {};
const ids = Object.keys(styles);

// Stable, deterministic order (sorted ids) so the generated file diffs cleanly across regens.
ids.sort();

const sectionCounts = { plain: 0, grid: 0, list: 0 };
const entries = ids.map((id) => {
  const s = styles[id];
  const name = s.name;
  const basedOn = s.basedOn == null ? null : String(s.basedOn);
  const section = sectionFor(name);
  sectionCounts[section]++;
  // JSON.stringify escapes each string safely (quotes, backslashes, the verbatim XML).
  const nameLit = JSON.stringify(name);
  const basedOnLit = basedOn === null ? 'null' : JSON.stringify(basedOn);
  const sectionLit = JSON.stringify(section);
  const xmlLit = JSON.stringify(String(s.xml));
  return `  ${JSON.stringify(id)}: { name: ${nameLit}, basedOn: ${basedOnLit}, section: ${sectionLit}, xml: ${xmlLit} },`;
});

const banner =
  `// AUTO-GENERATED from parity/oracle/table_style_defs.json — do not hand-edit.\n` +
  `// Regenerate: node scripts/gen-table-style-defs.js\n` +
  `// Source: real Word 16.0 locked-build per-style COM captures (113 defs). The XML is the\n` +
  `// verbatim <w:style> subtree (rsid stripped); parse per-use via the fork's public parseXmlToJson.\n`;

const type =
  `export const TABLE_STYLE_DEFS: Record<string, { name: string; basedOn: string | null; section: 'plain' | 'grid' | 'list'; xml: string }> = {\n`;

const body = entries.join('\n') + '\n';
const footer = `};\n`;

fs.writeFileSync(OUT, banner + '\n' + type + body + footer);

console.log('gen-table-style-defs: wrote ' + path.relative(ROOT, OUT));
console.log('  styles: ' + ids.length + ' (plain=' + sectionCounts.plain + ', grid=' + sectionCounts.grid + ', list=' + sectionCounts.list + ')');
