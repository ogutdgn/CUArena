// Document-level commands (file rename, future document settings).

import { useStore } from "./store";
import { dispatch, makeOpId } from "./dispatch";
import { emitSemantic } from "@/logger/semantic";

const MAX_FILE_NAME_LEN = 255;
const DEFAULT_FILE_NAME = "Untitled";

export function renameFile(after: string, trigger: "inline_edit" | "file_menu" = "inline_edit"): void {
  const s = useStore.getState();
  const before = s.document.name;
  let next = after.trim();
  if (next.length === 0) next = DEFAULT_FILE_NAME;
  if (next.length > MAX_FILE_NAME_LEN) next = next.slice(0, MAX_FILE_NAME_LEN);
  if (before === next) return;
  dispatch({
    id: makeOpId(),
    timestamp: performance.now(),
    kind: "set_document_name",
    before,
    after: next,
  });
  emitSemantic({ name: "rename_file", before, after: next, trigger });
}
