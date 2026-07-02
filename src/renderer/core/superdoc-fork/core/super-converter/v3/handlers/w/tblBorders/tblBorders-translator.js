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

// Property translators for w:tblBorders child elements
// Each translator handles a specific border property of the table
/** @type {import('@translator').NodeTranslator[]} */
const propertyTranslators = [
  wBottomTranslator,
  wEndTranslator,
  wInsideHTranslator,
  wInsideVTranslator,
  wLeftTranslator,
  wRightTranslator,
  wStartTranslator,
  wTopTranslator,
];

// MS-WORD-CLONE FORK EDIT (parity 032, user-authorized): CT_TblBorders (ECMA-376 §17.4.39) is an ordered
// xsd:sequence. decodeProperties emits children in the `borders` object's KEY-INSERTION order, so a
// programmatically-merged table border would export out of sequence. Passing this xmlOrder (the 6th
// createNestedPropertiesTranslator arg — same mechanism as TCPR_XML_ORDER in tcPr-translator.js) stable-sorts
// the children into schema order so emission can't be scrambled by insertion order. Imported nodes already
// arrive in order (no-op for them).
const TBLBORDERS_XML_ORDER = [
  'w:top', 'w:start', 'w:left', 'w:bottom', 'w:end', 'w:right', 'w:insideH', 'w:insideV', 'w:tl2br', 'w:tr2bl',
];

/**
 * The NodeTranslator instance for the tblBorders element.
 * @type {import('@translator').NodeTranslator}
 * @see {@link https://ecma-international.org/publications-and-standards/standards/ecma-376/} "Fundamentals And Markup Language Reference", page 422
 */
export const translator = NodeTranslator.from(
  createNestedPropertiesTranslator('w:tblBorders', 'borders', propertyTranslators, {}, [], TBLBORDERS_XML_ORDER),
);
