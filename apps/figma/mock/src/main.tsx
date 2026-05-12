import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@/theme/global.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { installRawCapture } from "@/logger/raw";
import { installPersist } from "@/logger/persist";
import { emitSemantic } from "@/logger/semantic";
import { downloadLogAsJson } from "@/logger/export";
import { installFixtureLoader } from "@/engine/fixture";

const persist = installPersist();
installRawCapture();
installFixtureLoader();

if (import.meta.env.DEV) {
  (window as any).__exportLog = downloadLogAsJson;
}
if (!persist.restored) {
  emitSemantic({
    name: "session_start",
    userAgent: navigator.userAgent,
    viewport: { width: window.innerWidth, height: window.innerHeight },
  });
}

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("No #root element found");

createRoot(rootEl).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
