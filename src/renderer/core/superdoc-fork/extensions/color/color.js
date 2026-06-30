// @ts-nocheck
import { Extension } from '@core/Extension.js';
import { cssColorToHex } from '@core/utilities/cssColorToHex.js';

/**
 * Color value format
 * @typedef {string} ColorValue
 * @description Accepts hex colors (#ff0000), rgb(255,0,0), or named colors (red)
 */

/**
 * Configuration options for Color
 * @typedef {Object} ColorOptions
 * @category Options
 * @property {string[]} [types=['textStyle']] Mark types to add color support to
 */

/**
 * Attributes for color marks
 * @typedef {Object} ColorAttributes
 * @category Attributes
 * @property {ColorValue} [color] Text color value
 * @example
 * // Apply color to selected text
 * editor.commands.setColor('#ff0000')
 *
 * // Remove color
 * editor.commands.unsetColor()
 */

/**
 * @module Color
 * @sidebarTitle Color
 * @snippetPath /snippets/extensions/color.mdx
 */
export const Color = Extension.create({
  name: 'color',

  addOptions() {
    return {
      types: ['textStyle'],
    };
  },

  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          color: {
            default: null,
            parseDOM: (el) => cssColorToHex(el.style.color),
            renderDOM: (attrs) => {
              if (!attrs.color) return {};
              return { style: `color: ${attrs.color}` };
            },
          },
          // Parity fix (spec 025): theme-color binding. Word writes <w:color w:val="HEX" w:themeColor="accentN"
          // [w:themeTint/w:themeShade]> for a Theme-Colors pick; the clone was sRGB-only (baked the resolved hex,
          // lost the theme link so it never recolored on theme change). These carry the link; the `color` attr
          // still supplies the visual hex. Pure model metadata — renderDOM uses a data-* attr so in-app copy/paste
          // preserves it, but the docx export reads the mark attrs directly (decodeRPrFromMarks / translateMark).
          themeColor: {
            default: null,
            parseDOM: (el) => (el.getAttribute && el.getAttribute('data-theme-color')) || null,
            renderDOM: (attrs) => (attrs.themeColor ? { 'data-theme-color': attrs.themeColor } : {}),
          },
          themeTint: {
            default: null,
            parseDOM: (el) => (el.getAttribute && el.getAttribute('data-theme-tint')) || null,
            renderDOM: (attrs) => (attrs.themeTint ? { 'data-theme-tint': attrs.themeTint } : {}),
          },
          themeShade: {
            default: null,
            parseDOM: (el) => (el.getAttribute && el.getAttribute('data-theme-shade')) || null,
            renderDOM: (attrs) => (attrs.themeShade ? { 'data-theme-shade': attrs.themeShade } : {}),
          },
        },
      },
    ];
  },

  addCommands() {
    return {
      /**
       * Set text color
       * @category Command
       * @param {ColorValue} color - Color value to apply
       * @example
       * // Set to red using hex
       * editor.commands.setColor('#ff0000')
       *
       * @example
       * // Set using rgb
       * editor.commands.setColor('rgb(255, 0, 0)')
       *
       * @example
       * // Set using named color
       * editor.commands.setColor('blue')
       * @note Preserves other text styling attributes
       */
      setColor:
        (color, options = {}) =>
        ({ chain }) => {
          // Parity fix (spec 025): an optional theme binding from a Theme-Colors pick. setMark writes the keys
          // UNCONDITIONALLY (null when absent) so switching from a theme swatch to a plain/custom color CLEARS a
          // stale themeColor instead of leaving it attached to the new hex.
          const attrs = {
            color,
            themeColor: options.themeColor ?? null,
            themeTint: options.themeTint ?? null,
            themeShade: options.themeShade ?? null,
          };
          return chain().setMark('textStyle', attrs).run();
        },

      /**
       * Remove text color
       * @category Command
       * @example
       * editor.commands.unsetColor()
       * @note Removes color while preserving other text styles
       */
      unsetColor:
        () =>
        ({ chain }) => {
          return chain()
            .setMark('textStyle', { color: null, themeColor: null, themeTint: null, themeShade: null })
            .removeEmptyTextStyle()
            .run();
        },
    };
  },
});
