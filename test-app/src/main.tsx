import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@/theme/global.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { installRawCapture } from "@/logger/raw";
import { emitSemantic } from "@/logger/semantic";

installRawCapture();
emitSemantic({
  name: "session_start",
  userAgent: navigator.userAgent,
  viewport: { width: window.innerWidth, height: window.innerHeight },
});

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("No #root element found");

createRoot(rootEl).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
