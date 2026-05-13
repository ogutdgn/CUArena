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

async function maybeAutoLoadFixture(): Promise<void> {
  const shouldAutoLoad = import.meta.env.VITE_AUTO_FIXTURE === "1";
  if (!shouldAutoLoad) return;

  try {
    const response = await fetch("/__fixture_bootstrap__.json", { cache: "no-store" });
    if (!response.ok) {
      console.warn(`[fixture] auto-load skipped; HTTP ${response.status}`);
      return;
    }
    const payload = await response.json();
    const loader = (window as any).__loadFixture;
    if (typeof loader !== "function") {
      console.warn("[fixture] auto-load skipped; loader unavailable");
      return;
    }
    const ok = loader(payload);
    if (!ok) {
      console.warn("[fixture] auto-load failed; hydrate rejected fixture");
    }
  } catch (error) {
    console.warn("[fixture] auto-load error", error);
  }
}

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

void maybeAutoLoadFixture().finally(() => {
  createRoot(rootEl).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
});
