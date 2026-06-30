import { parseBoolean, booleanToString } from '@converter/v3/handlers/utils.js';
import { NodeTranslator } from '@translator';

/**
 * The NodeTranslator instance for the w:caps element.
 * @type {import('@translator').NodeTranslator}
 * @see {@link https://ecma-international.org/publications-and-standards/standards/ecma-376/} "Fundamentals And Markup Language Reference", page 267
 */
export const translator = NodeTranslator.from({
  xmlName: 'w:caps',
  sdNodeOrKeyName: 'textTransform',
  encode: ({ nodes }) => (parseBoolean(nodes[0].attributes?.['w:val'] ?? '1') ? 'uppercase' : 'none'),
  decode: ({ node }) => {
    const tt = node.attrs['textTransform'];
    if (tt == null) return undefined;
    // Parity fix (spec 024): on ON, emit a BARE <w:caps/> like Word (and like the strike/smallCaps boolean
    // handlers) instead of the redundant <w:caps w:val="1"/>; keep an explicit <w:caps w:val="0"/> for OFF so a
    // turned-off-against-inheritance state stays distinguishable. encode treats a missing w:val as '1' (round-trips).
    return tt === 'uppercase'
      ? { name: 'w:caps', attributes: {} }
      : { name: 'w:caps', attributes: { 'w:val': booleanToString(false) } };
  },
});
