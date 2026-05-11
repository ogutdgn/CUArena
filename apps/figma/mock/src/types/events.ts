// Closed semantic event registry. schemaVersion = 1.
// Source: .analysis/engine-report.md §5.
// Adding new events bumps minor; payload changes to existing events bump major.

export const SCHEMA_VERSION = 1;

export interface SemanticEventBase {
  schemaVersion: 1;
  sessionId: string;
  eventId: string;
  timestamp: number;
  pageId: string | null;
  rawEventIdRange: [string, string] | null;
}

export type SelectionTriggerMethod =
  | "click_select"
  | "shift_click_add"
  | "shift_click_remove"
  | "drag_box_select"
  | "select_all"
  | "deselect"
  | "implicit_after_create"
  | "implicit_after_delete"
  | "implicit_after_paste"
  | "implicit_after_duplicate"
  | "implicit_after_group"
  | "implicit_after_ungroup"
  | "implicit_after_undo"
  | "implicit_after_redo"
  | "panel_row_click"
  | "page_switch";

// ---- Slice 0 events (full set in slice 1+; declared here for forward-compat) ----

export type SemanticEvent =
  | (SemanticEventBase & {
      name: "tool_change";
      before: string;
      after: string;
      trigger: "shortcut" | "toolbar_click" | "auto_revert_after_create" | "space_temp_hand";
    })
  | (SemanticEventBase & {
      name: "mode_change";
      before: string;
      after: string;
    })
  | (SemanticEventBase & {
      name: "selection_change";
      before: string[];
      after: string[];
      triggerMethod: SelectionTriggerMethod;
      cause: { eventId: string } | null;
    })
  | (SemanticEventBase & {
      name: "click_select";
      targetLayerId: string | null;
      pointer: { x: number; y: number };
      source: "canvas" | "layers_panel";
    })
  | (SemanticEventBase & {
      name: "shift_click_add_selection";
      targetLayerId: string;
      pointer: { x: number; y: number };
      source: "canvas" | "layers_panel";
    })
  | (SemanticEventBase & {
      name: "shift_click_remove_selection";
      targetLayerId: string;
      pointer: { x: number; y: number };
      source: "canvas" | "layers_panel";
    })
  | (SemanticEventBase & {
      name: "drag_box_select";
      start: { x: number; y: number };
      end: { x: number; y: number };
      layerIds: string[];
      modifier: "none" | "shift_additive" | "alt_enclosure";
    })
  | (SemanticEventBase & {
      name: "select_all";
      scope: "page" | "parent_group" | "parent_frame";
      layerIds: string[];
    })
  | (SemanticEventBase & {
      name: "deselect";
      trigger: "escape" | "click_empty_canvas" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "create_rectangle";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut_R" | "toolbar" | "click_default_size";
    })
  | (SemanticEventBase & {
      name: "create_ellipse";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut_O" | "toolbar" | "click_default_size";
    })
  | (SemanticEventBase & {
      name: "create_polygon";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      sides: number;
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut" | "toolbar" | "click_default_size";
    })
  | (SemanticEventBase & {
      name: "create_star";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      points: number;
      innerRatio: number;
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut" | "toolbar" | "click_default_size";
    })
  | (SemanticEventBase & {
      name: "create_line";
      layerId: string;
      p1: { x: number; y: number };
      p2: { x: number; y: number };
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut_L" | "toolbar";
    })
  | (SemanticEventBase & {
      name: "create_arrow";
      layerId: string;
      p1: { x: number; y: number };
      p2: { x: number; y: number };
      parentId: string;
      modifiers: { shift: boolean; alt: boolean };
      trigger: "shortcut_shift_L" | "toolbar";
    })
  | (SemanticEventBase & {
      name: "create_frame";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      mode: "drag" | "preset" | "wrap";
      trigger: "shortcut_F" | "toolbar" | "preset" | "wrap_selection";
    })
  | (SemanticEventBase & {
      name: "create_section";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      trigger: "shortcut_shift_S" | "toolbar" | "wrap_selection";
    })
  | (SemanticEventBase & {
      name: "create_slice";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      trigger: "shortcut" | "toolbar";
    })
  | (SemanticEventBase & {
      name: "create_text";
      layerId: string;
      x: number;
      y: number;
      w: number;
      h: number;
      parentId: string;
      resizingMode: "auto_width" | "auto_height" | "fixed";
      trigger: "shortcut_T" | "toolbar";
    })
  | (SemanticEventBase & {
      name: "place_image";
      layerIds: string[];
      source: "file_picker" | "drag_drop" | "clipboard_paste";
      filenames: string[];
    })
  | (SemanticEventBase & {
      name: "type_characters";
      layerId: string;
      length: number;
    })
  | (SemanticEventBase & {
      name: "commit_text";
      layerId: string;
      content: string;
    })
  | (SemanticEventBase & {
      name: "create_vector_with_pen";
      layerId: string;
      closed: boolean;
      pointCount: number;
    })
  | (SemanticEventBase & {
      name: "add_vector_point";
      layerId: string;
      index: number;
      position: { x: number; y: number };
    })
  | (SemanticEventBase & {
      name: "move_vector_point";
      layerId: string;
      index: number;
      before: { x: number; y: number };
      after: { x: number; y: number };
    })
  | (SemanticEventBase & {
      name: "delete_vector_point";
      layerId: string;
      index: number;
    })
  | (SemanticEventBase & {
      name: "create_vector_with_pencil";
      layerId: string;
      pointCount: number;
    })
  | (SemanticEventBase & {
      name: "align_layers";
      layerIds: string[];
      axis: "left" | "center-x" | "right" | "top" | "center-y" | "bottom";
      trigger: "panel_button" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "distribute_layers";
      layerIds: string[];
      axis: "horizontal" | "vertical";
      trigger: "panel_button" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "tidy_up";
      layerIds: string[];
      // Detected layout for the selection. 1D = single row/column with
      // overlapping perpendicular extents; 2D = multi-row/column grid.
      dimension: "1d_horizontal" | "1d_vertical" | "2d";
      // Resolved spacing in px. 1D fills only the primary axis; 2D fills both.
      computedSpacing: { x?: number; y?: number };
      trigger: "panel_button" | "context_menu" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "set_page_background";
      targetPageId: string;
      before: { r: number; g: number; b: number; a: number };
      after: { r: number; g: number; b: number; a: number };
      trigger?: "color_picker" | "hex_input";
    })
  | (SemanticEventBase & {
      name: "set_page_background_opacity";
      targetPageId: string;
      before: number;
      after: number;
      trigger: "panel_input";
    })
  | (SemanticEventBase & {
      name: "toggle_page_background_hidden";
      targetPageId: string;
      before: boolean;
      after: boolean;
      trigger: "panel_button";
    })
  | (SemanticEventBase & {
      name: "move_layer";
      layerIds: string[];
      before: Record<string, { x: number; y: number }>;
      after: Record<string, { x: number; y: number }>;
      trigger: "drag" | "arrow_key" | "panel_input";
      modifiers: { shift: boolean; alt: boolean; ctrl: boolean };
    })
  | (SemanticEventBase & {
      name: "resize_layer";
      layerIds: string[];
      before: Record<string, { x: number; y: number; w: number; h: number }>;
      after: Record<string, { x: number; y: number; w: number; h: number }>;
      handle: "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";
      trigger: "drag" | "panel_input";
      modifiers: { shift: boolean; alt: boolean };
    })
  | (SemanticEventBase & {
      name: "resize_line_endpoint";
      layerId: string;
      endpoint: "p1" | "p2";
      before: {
        transform: { x: number; y: number; w: number; h: number; rotation: number; scaleX: number; scaleY: number };
        p1: { x: number; y: number };
        p2: { x: number; y: number };
      };
      after: {
        transform: { x: number; y: number; w: number; h: number; rotation: number; scaleX: number; scaleY: number };
        p1: { x: number; y: number };
        p2: { x: number; y: number };
      };
      trigger: "drag";
    })
  | (SemanticEventBase & {
      name: "delete";
      layerIds: string[];
      trigger:
        | "keyboard_canvas"
        | "keyboard_panel"
        | "context_menu_canvas"
        | "context_menu_panel"
        | "main_menu";
    })
  | (SemanticEventBase & {
      name: "copy";
      layerIds: string[];
      trigger: "shortcut" | "context_menu" | "main_menu";
    })
  | (SemanticEventBase & {
      name: "cut";
      layerIds: string[];
      trigger: "shortcut" | "context_menu" | "main_menu";
    })
  | (SemanticEventBase & {
      name: "paste";
      newLayerIds: string[];
      placement: "viewport_center" | "into_frame" | "at_cursor" | "from_origin";
      trigger: "shortcut" | "context_menu" | "main_menu";
    })
  | (SemanticEventBase & {
      name: "duplicate";
      sourceLayerIds: string[];
      newLayerIds: string[];
      offset: { dx: number; dy: number };
      trigger: "shortcut_cmd_d" | "alt_drag";
    })
  | (SemanticEventBase & {
      name: "pan_canvas";
      delta: { dx: number; dy: number };
      before: { x: number; y: number };
      after: { x: number; y: number };
      trigger: "space_drag" | "hand_tool_drag" | "trackpad" | "arrow_key" | "middle_mouse";
    })
  | (SemanticEventBase & {
      name: "zoom_canvas";
      before: number;
      after: number;
      anchor: { x: number; y: number };
      trigger: "scroll" | "pinch" | "keyboard" | "input_field" | "dropdown_entry" | "magic_mouse";
    })
  | (SemanticEventBase & {
      name: "viewport_change";
      before: { x: number; y: number; zoom: number };
      after: { x: number; y: number; zoom: number };
      reasons: Array<"pan" | "zoom">;
    })
  | (SemanticEventBase & {
      name: "zoom_to_fit";
      contentBounds: { x: number; y: number; w: number; h: number } | null;
      trigger: "keyboard" | "dropdown_entry" | "initial_load";
    })
  | (SemanticEventBase & {
      name: "zoom_to_100";
      trigger: "keyboard" | "input_field";
    })
  | (SemanticEventBase & {
      name: "zoom_to_selection";
      selectionBounds: { x: number; y: number; w: number; h: number };
      layerIds: string[];
      trigger: "keyboard" | "dropdown_entry";
    })
  | (SemanticEventBase & {
      name: "undo";
      revertedOpKind: string;
      revertedOpId: string;
    })
  | (SemanticEventBase & {
      name: "redo";
      reappliedOpKind: string;
      reappliedOpId: string;
    })
  | (SemanticEventBase & {
      name: "noop_click";
      elementId: string;
      pointer: { x: number; y: number };
    })
  | (SemanticEventBase & {
      name: "rotate_layer";
      layerIds: string[];
      before: Record<string, number>;
      after: Record<string, number>;
      trigger: "drag" | "panel_input" | "panel_button";
    })
  | (SemanticEventBase & {
      name: "flip_layer";
      layerIds: string[];
      axis: "horizontal" | "vertical";
      trigger: "shortcut" | "context_menu" | "main_menu" | "panel_button";
    })
  | (SemanticEventBase & {
      name: "scale_layer";
      layerIds: string[];
      factor: { sx: number; sy: number };
      anchor: { x: number; y: number };
      trigger: "drag";
    })
  | (SemanticEventBase & {
      name: "set_property";
      layerIds: string[];
      path: string;
      before: Record<string, unknown>;
      after: Record<string, unknown>;
      trigger: "panel_input" | "color_picker" | "context_menu" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "set_fill_color";
      layerIds: string[];
      fillIndex: number;
      before: { r: number; g: number; b: number; a: number };
      after: { r: number; g: number; b: number; a: number };
    })
  | (SemanticEventBase & {
      name: "add_fill" | "remove_fill";
      layerIds: string[];
      fillIndex: number;
    })
  | (SemanticEventBase & {
      name: "toggle_layer_visibility" | "toggle_fill_visibility" | "toggle_stroke_visibility" | "toggle_effect_visibility";
      layerIds: string[];
      index?: number;
      after: boolean;
    })
  | (SemanticEventBase & {
      name: "set_layer_opacity";
      layerIds: string[];
      before: Record<string, number>;
      after: Record<string, number>;
      trigger: "slider_scrub" | "panel_input";
    })
  | (SemanticEventBase & {
      name: "set_corner_radius";
      layerIds: string[];
      before: Record<string, number | [number, number, number, number]>;
      after: Record<string, number | [number, number, number, number]>;
      trigger: "slider_scrub" | "panel_input";
    })
  | (SemanticEventBase & {
      name: "rename_layer";
      layerId: string;
      before: string;
      after: string;
      trigger: "inline_panel" | "rename_modal" | "context_menu";
    })
  | (SemanticEventBase & {
      name: "group_selection" | "ungroup";
      layerIds: string[];
      groupId?: string;
      trigger: "shortcut" | "context_menu" | "main_menu";
    })
  | (SemanticEventBase & {
      name: "enter_group" | "exit_group";
      groupId: string;
    })
  | (SemanticEventBase & {
      name: "reorder_layer";
      layerIds: string[];
      before: { parentId: string; index: number }[];
      after: { parentId: string; index: number }[];
      trigger:
        | "shortcut_cmd_close_bracket"
        | "shortcut_cmd_open_bracket"
        | "shortcut_cmd_alt_close_bracket"
        | "shortcut_cmd_alt_open_bracket"
        | "panel_drag"
        | "canvas_drag";
    })
  | (SemanticEventBase & {
      name: "create_page";
      newPageId: string;
      pageIndex: number;
      trigger: "panel_button" | "context_menu";
    })
  | (SemanticEventBase & {
      name: "switch_page";
      beforePageId: string;
      afterPageId: string;
      trigger: "panel_click" | "shortcut" | "implicit_after_create";
    })
  | (SemanticEventBase & {
      name: "rename_page";
      targetPageId: string;
      before: string;
      after: string;
    })
  | (SemanticEventBase & {
      name: "rename_file";
      before: string;
      after: string;
      trigger: "inline_edit" | "file_menu";
    })
  | (SemanticEventBase & {
      name: "set_polygon_sides";
      layerIds: string[];
      before: Record<string, number>;
      after: Record<string, number>;
      trigger: "panel_input";
    })
  | (SemanticEventBase & {
      name: "set_star_points";
      layerIds: string[];
      before: Record<string, number>;
      after: Record<string, number>;
      trigger: "panel_input";
    })
  | (SemanticEventBase & {
      name: "set_star_inner_ratio";
      layerIds: string[];
      before: Record<string, number>;
      after: Record<string, number>;
      trigger: "panel_input";
    })
  | (SemanticEventBase & {
      name: "delete_page";
      targetPageId: string;
      pageIndex: number;
      trigger: "context_menu" | "shortcut";
    })
  | (SemanticEventBase & {
      name: "session_start";
      userAgent: string;
      viewport: { width: number; height: number };
    })
  | (SemanticEventBase & {
      name: "session_end";
    })
  // ---- Prototype events ----
  | (SemanticEventBase & {
      name: "prototype_tab_switch";
      before: "design" | "prototype";
      after: "design" | "prototype";
      trigger: "tab_click" | "shortcut_shift_e";
    })
  | (SemanticEventBase & {
      name: "set_prototype_device";
      before: string | null;
      after: string | null;
    })
  | (SemanticEventBase & {
      name: "open_prototype_preview";
      trigger: "play_button";
    })
  | (SemanticEventBase & {
      name: "close_prototype_preview";
      trigger: "close_button" | "play_button_toggle";
    })
  | (SemanticEventBase & {
      name: "navigate_prototype_preview";
      direction: "prev" | "next";
      fromIndex: number;
      toIndex: number;
    })
  | (SemanticEventBase & {
      name: "create_prototype_connection";
      connectionId: string;
      sourceLayerId: string;
      trigger: string;
      action: string;
    })
  | (SemanticEventBase & {
      name: "delete_prototype_connection";
      connectionId: string;
      sourceLayerId: string;
    })
  | (SemanticEventBase & {
      name: "update_prototype_connection";
      connectionId: string;
      field: "trigger" | "action" | "destinationFrameId" | "animation" | "delayMs" | "url";
      before: string | null;
      after: string | null;
    })
  | (SemanticEventBase & {
      name: "navigate_prototype_connection";
      connectionId: string;
      sourceLayerId: string;
      destinationFrameId: string;
    });

export type SemanticEventName = SemanticEvent["name"];

// Distributive Omit — each union member keeps its discriminator + member-specific fields.
export type SemanticEventInput<E extends SemanticEvent = SemanticEvent> = E extends unknown
  ? Omit<E, "schemaVersion" | "sessionId" | "eventId" | "timestamp" | "pageId" | "rawEventIdRange">
  : never;

// ---- Raw event schema ----

export interface RawEvent {
  eventId: string;
  type: string;
  timestamp: number;
  sessionTime: number;
  fields: Record<string, unknown>;
  targetId: string | null;
  modifiers: { alt: boolean; shift: boolean; ctrl: boolean; meta: boolean };
}
