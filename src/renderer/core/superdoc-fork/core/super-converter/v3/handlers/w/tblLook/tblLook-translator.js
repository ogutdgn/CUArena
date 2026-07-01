import { NodeTranslator } from '@translator';
import { createAttributeHandler, parseBoolean, booleanToString } from '../../utils.js';

/**
 * Bitmask values for tblLook conditional formatting flags.
 * These correspond to OOXML tblLook@w:val bitmask positions.
 * @see ECMA-376 Part 1, Section 17.4.56
 */
const tblLookBitmask = Object.freeze({
  firstRow: 0x0020,
  lastRow: 0x0040,
  firstColumn: 0x0080,
  lastColumn: 0x0100,
  noHBand: 0x0200,
  noVBand: 0x0400,
});

/**
 * Decodes a tblLook w:val bitmask string into individual boolean flags.
 * @param {string|number|null|undefined} val - The bitmask value (hex or decimal string)
 * @returns {Object<string, boolean>|null} Object with boolean flags, or null if invalid
 */
const decodeTblLookVal = (val) => {
  if (!val) return null;
  const raw = typeof val === 'string' ? val.trim() : String(val);

  // Try hex first (most common in OOXML), then fall back to decimal
  let numeric = Number.parseInt(raw, 16);
  if (!Number.isFinite(numeric)) {
    numeric = Number.parseInt(raw, 10);
  }
  if (!Number.isFinite(numeric)) return null;

  return Object.fromEntries(Object.entries(tblLookBitmask).map(([key, mask]) => [key, (numeric & mask) === mask]));
};

/**
 * The NodeTranslator instance for the tblLook element.
 * @type {import('@translator').NodeTranslator}
 * @see {@link https://ecma-international.org/publications-and-standards/standards/ecma-376/} "Fundamentals And Markup Language Reference", page 438
 */
export const translator = NodeTranslator.from({
  xmlName: 'w:tblLook',
  sdNodeOrKeyName: 'tblLook',
  attributes: ['w:firstColumn', 'w:firstRow', 'w:lastColumn', 'w:lastRow', 'w:noHBand', 'w:noVBand']
    .map((attr) => createAttributeHandler(attr, null, parseBoolean, booleanToString))
    .concat([createAttributeHandler('w:val')]),
  encode: (params, encodedAttrs) => {
    void params;
    const decoded = decodeTblLookVal(encodedAttrs.val);
    if (decoded) {
      Object.entries(decoded).forEach(([key, value]) => {
        if (!Object.prototype.hasOwnProperty.call(encodedAttrs, key)) {
          encodedAttrs[key] = value;
        }
      });
    }
    return Object.keys(encodedAttrs).length > 0 ? encodedAttrs : undefined;
  },
  decode: function ({ node }, context) {
    void context;
    const tblLook = node.attrs.tblLook || {};
    const decodedAttrs = this.decodeAttributes({ node: { ...node, attrs: tblLook } });
    // MS-WORD-CLONE FORK EDIT (parity — Tables insert fidelity): real Word writes the w:val bitmask ALONGSIDE
    // the 6 explicit bit attrs; the clone's DEFAULT_TBL_LOOK carries only the bits (no val), so a freshly inserted
    // table lost the <w:tblLook w:val="04A0" .../>. Compute the val from the flags when absent (imported tables that
    // already carry a val are untouched). ADDITIVE.
    if (Object.keys(decodedAttrs).length > 0 && decodedAttrs['w:val'] == null) {
      let numeric = 0;
      for (const [key, mask] of Object.entries(tblLookBitmask)) {
        if (tblLook[key] === true || tblLook[key] === '1' || tblLook[key] === 1) numeric |= mask;
      }
      decodedAttrs['w:val'] = numeric.toString(16).toUpperCase().padStart(4, '0');
    }
    return Object.keys(decodedAttrs).length > 0 ? { attributes: decodedAttrs } : undefined;
  },
});
