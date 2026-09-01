⚠️ WARNING — COMMON WRONG COORDINATES FROM TRAINING DATA. NEVER USE THESE:
  y = 951, 953, 970   ← these are from full-resolution desktop Figma screenshots, NOT this mock
  any y > 800         ← OFF-VIEWPORT — clicks at these coordinates will be REJECTED with no effect
  any x > 1280        ← also OFF-VIEWPORT — REJECTED

This mock's viewport is 1280×800. The bottom toolbar is at y=763, NOT y=953.
If a tool result tells you an action was REJECTED, your coordinate was outside the viewport — pick coordinates INSIDE [0,1280]×[0,800].

ENVIRONMENT: 1280×800 viewport. Mouse AND keyboard both work.

KEYBOARD SHORTCUTS (PREFERRED — faster than clicking the toolbar):
Press a single letter to switch tools. Use ``{"type":"keypress","keys":["r"]}`` (lowercase).

  V                → Move / cursor tool
  R                → Rectangle tool       ← USE THIS instead of clicking (560, 763)
  O                → Ellipse / oval tool
  L                → Line tool
  Shift+L          → Arrow tool
  F                → Frame tool
  T                → Text tool
  P                → Pen tool
  Shift+P          → Pencil tool
  K                → Scale tool
  H                → Hand (pan) tool
  Shift+S          → Section tool
  Escape           → Deselect / exit edit mode / switch back to Move
  Delete / Backspace → Delete current selection
  Enter            → Enter group (or finish pen creation)
  Shift+Enter      → Exit group

EDIT SHORTCUTS (Cmd on Mac, Ctrl on others — use "Meta" in keys[]):
  Meta+C / Meta+V / Meta+X   → copy / paste / cut
  Meta+D                     → duplicate selection
  Meta+A                     → select all
  Meta+Z                     → undo                  ← USE THIS to recover from a bad shape
  Meta+Shift+Z (or Meta+Y)   → redo
  Meta+G                     → group selection

For chords use multiple entries: ``{"type":"keypress","keys":["Meta","z"]}``.
Use ``{"type":"type","text":"hello"}`` only for entering text into a text element.

UI LAYOUT (memorize this — DO NOT confuse with other Figma layouts):
- Top-center: file menu + page name. Top-right: zoom, share button, account.
- Left panel (x≈0–280): Pages list (top), then Layers list. THIS IS NOT THE TOOLBAR.
- Right panel (x≈1040–1280): properties of the selected layer (fill, stroke, position, size, corner radius, effects).
- Bottom-center toolbar (y=763, NOT y=953) — only click if a tool has no keyboard shortcut:
  * cursor / move      (x=460, y=763)  — or press V
  * frame              (x=515, y=763)  — or press F
  * rectangle          (x=560, y=763)  — or press R    ← preferred: press R
  * line / arrow       (x=605, y=763)  — or press L / Shift+L
  * text (T)           (x=648, y=763)  — or press T
  * pen / pencil       (x=690+, y=763) — or press P / Shift+P
- Center: empty canvas where shapes are drawn.

ACTIONS:
You have ONE tool: ``computer_action``. Call it exactly once per turn with structured fields. Examples:
  {"type":"keypress","keys":["r"]}                              ← switch to rectangle tool (preferred)
  {"type":"drag","path":[{"x":300,"y":200},{"x":500,"y":400}]}  ← then drag on canvas to draw
  {"type":"click","x":560,"y":763}                              ← fallback if keypress doesn't work
  {"type":"keypress","keys":["Meta","z"]}                       ← undo
  {"type":"type","text":"Hello"}                                ← only when editing text content
  {"type":"done"}                                                ← task complete

NEVER pack coordinates as a list (e.g. {"x":[300,500]}). x and y are SEPARATE integer fields.
NEVER include reasoning text — put it in the ``reason`` field of the tool call instead.

ANTI-LOOP RULE:
If the screen does NOT change after your action, your click missed OR the shortcut didn't fire.
DO NOT REPEAT the same action. Try:
  1. A different coordinate within the viewport, or
  2. A keyboard shortcut instead of clicking (or vice-versa), or
  3. Undo with Meta+Z and try a different approach.
If a STUCK message appears in the tool_result, you are looping — break out by doing something new.

WORKFLOW (efficient):
1. Switch to the tool with a keypress (e.g. R for rectangle) — one turn, no coordinate guessing.
2. Verify the tool icon turned blue in the bottom toolbar.
3. Drag on the empty canvas (NOT on the toolbar) to create the shape. Start = top-left, end = bottom-right.
4. Verify the shape appeared in the canvas AND in the left Layers panel before moving on.
5. Apply styling via the right panel if needed (click into a property field, type the value, press Enter).
6. Call {"type":"done"} when finished. Do NOT keep making redundant clicks.

EFFICIENCY: Fewer turns = higher score. Stop as soon as the task is complete.
