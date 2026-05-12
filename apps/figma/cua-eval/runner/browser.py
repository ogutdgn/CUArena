"""Playwright wrapper for CUA agent runs.

Boots a Chromium against the running mock, exposes screenshot + action
primitives, and scrapes the three sessionStorage log streams at the end of
the attempt to reconstruct the full log payload.
"""
from __future__ import annotations

import base64
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 800


@dataclass
class BrowserSession:
    page: Page
    context: BrowserContext
    browser: Browser

    def screenshot_b64(self) -> str:
        png = self.page.screenshot(type="png", full_page=False)
        return base64.standard_b64encode(png).decode("ascii")

    def click(self, x: int, y: int, button: str = "left", click_count: int = 1) -> None:
        self.page.mouse.click(x, y, button=button, click_count=click_count)

    def double_click(self, x: int, y: int) -> None:
        self.page.mouse.dblclick(x, y)

    def move(self, x: int, y: int) -> None:
        self.page.mouse.move(x, y)

    def drag(self, path: list[tuple[int, int]]) -> None:
        if not path:
            return
        x0, y0 = path[0]
        self.page.mouse.move(x0, y0)
        self.page.mouse.down()
        for x, y in path[1:]:
            self.page.mouse.move(x, y, steps=10)
        self.page.mouse.up()

    def scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self.page.mouse.move(x, y)
        self.page.mouse.wheel(dx, dy)

    def type_text(self, text: str) -> None:
        self.page.keyboard.type(text, delay=10)

    def key(self, keys: str) -> None:
        # Accept either a single key ("Enter") or a "+"-joined chord ("Control+a").
        # Playwright's press() understands chords with "+".
        self.page.keyboard.press(keys)

    def wait(self, ms: int) -> None:
        self.page.wait_for_timeout(ms)

    def load_fixture(self, fixture_dict: dict) -> bool:
        """Inject a fixture into the mock via window.__loadFixture.

        fixture_dict should have 'frame' and 'layers' keys matching the
        Fixture dataclass in verifier/types.py.
        """
        self.page.wait_for_timeout(300)
        result = self.page.evaluate(
            """(fixture) => {
                if (typeof window.__loadFixture !== 'function') {
                    return false;
                }
                return window.__loadFixture(fixture);
            }""",
            fixture_dict,
        )
        self.page.wait_for_timeout(500)
        return bool(result)

    def scrape_log(self) -> dict:
        """Reconstruct the unified log from local/sessionStorage. Returns
        the same shape that the Vite /dev-log relay would have POSTed.

        Mock prefers localStorage (mock/src/logger/persist.ts:resolveStorage),
        falling back to sessionStorage when localStorage is blocked. We
        check both so the scrape works regardless of which the mock chose.
        """
        # Let the 250ms persist throttle settle.
        self.page.wait_for_timeout(750)
        bundle = self.page.evaluate(
            """() => {
                const out = { raw: null, semantic: null, outcome: null, sessionId: null };
                const stores = [];
                try { if (typeof localStorage !== 'undefined') stores.push(localStorage); } catch (e) {}
                try { if (typeof sessionStorage !== 'undefined') stores.push(sessionStorage); } catch (e) {}
                for (const store of stores) {
                    for (let i = 0; i < store.length; i++) {
                        const k = store.key(i);
                        if (!k || !k.endsWith('_data')) continue;
                        const v = store.getItem(k);
                        if (v == null) continue;
                        if (k.includes('_raw_')) {
                            // Prefer the latest raw key (later iterations win).
                            out.raw = v;
                            out.sessionId = k.split('_raw_')[1].replace('_data','');
                        } else if (k.includes('_semantic_')) {
                            out.semantic = v;
                        } else if (k.includes('_outcome_')) {
                            out.outcome = v;
                        }
                    }
                    // If this store had data, don't overwrite from the next one.
                    if (out.raw || out.semantic || out.outcome) break;
                }
                return out;
            }"""
        )
        return {
            "schemaVersion": 1,
            "sessionId": bundle.get("sessionId") or "",
            "exportedAt": int(time.time() * 1000),
            "raw": json.loads(bundle.get("raw") or "[]"),
            "semantic": json.loads(bundle.get("semantic") or "[]"),
            "outcome": json.loads(bundle.get("outcome") or "{}"),
        }


@contextmanager
def launch_browser(mock_url: str, headless: bool = True) -> Iterator[BrowserSession]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": DISPLAY_WIDTH, "height": DISPLAY_HEIGHT},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto(mock_url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        try:
            yield BrowserSession(page=page, context=context, browser=browser)
        finally:
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass
