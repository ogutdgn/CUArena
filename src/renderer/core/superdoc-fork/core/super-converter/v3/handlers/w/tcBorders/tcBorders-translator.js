import { NodeTranslator } from '@translator';
import { createNestedPropertiesTranslator } from '../../utils.js';
import { translator as wBottomTranslator } from '../bottom';
import { translator as wEndTranslator } from '../end';
import { translator as wInsideHTranslator } from '../insideH';
import { translator as wInsideVTranslator } from '../insideV';
import { translator as wLeftTranslator } from '../left';
import { translator as wRightTranslator } from '../right';
import { translator as wStartTranslator } from '../start';
import { translator as wTopTranslator } from '../top';
import { translator as tl2brTranslator } from '@converter/v3/handlers/w/tl2br';
import { translator as tr2blTranslator } from '@converter/v3/handlers/w/tr2bl';

// Property translators for w:tcBorders child elements
// Each translator handles a specific border property of the table
/** @type {import('@translator').NodeTranslator[]} */
const propertyTranslators = [
  wTopTranslator,
  wStartTranslator,
  wLeftTranslator,
  wBottomTranslator,
  wEndTranslator,
  wRightTranslator,
  wInsideHTranslator,
  wInsideVTranslator,
  tl2brTranslator,
  tr2blTranslator,
];

// MS-WORD-CLONE FORK EDIT (parity 032, user-authorized): CT_TcBorders (ECMA-376 §17.4.66) is an ordered
// xsd:sequence. decodeProperties emits children in the `borders` object's KEY-INSERTION order, so a
// programmatically-merged border (e.g. the Borders dropdown adds `bottom` after `top`, or a diagonal after
// the edges) would export out of sequence. Passing this xmlOrder (the 6th createNestedPropertiesTranslator
// arg — same mechanism as TCPR_XML_ORDER in tcPr-translator.js) stable-sorts the children into schema order
// so emission can't be scrambled by insertion order. Imported cells already arrive in order (no-op for them).
const TCBORDERS_XML_ORDER = [
  'w:top', 'w:start', 'w:left', 'w:bottom', 'w:end', 'w:right', 'w:insideH', 'w:insideV', 'w:tl2br', 'w:tr2bl',
];

/**
 * The NodeTranslator instance for the tcBorders element.
 * @type {import('@translator').NodeTranslator}
 * @see {@link https://ecma-international.org/publications-and-standards/standards/ecma-376/} "Fundamentals And Markup Language Reference", page 459
 */
export const translator = NodeTranslator.from(
  createNestedPropertiesTranslator('w:tcBorders', 'borders', propertyTranslators, {}, [], TCBORDERS_XML_ORDER),
);
