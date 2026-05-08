"""
Focused QA checks for verifier framework primitives that are not exercised by
delivery-1's synthetic task smoke tests.

Usage:
    ../.venv/Scripts/python scripts/qa_verifier_framework.py
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_ROOT))

from verifier.checks.geometry_checks import (  # noqa: E402
    LayerCenterPosition,
    LineAngleEquals,
    LineLengthEquals,
    LinesShareEndpoint,
)
from verifier.checks.page_checks import (  # noqa: E402
    DocumentNameEquals,
    PageBackgroundHiddenIs,
    PageBackgroundOpacityEquals,
    PrototypeConnectionExists,
)


def _log(document: dict) -> dict:
    return {
        "semantic": [],
        "outcome": {
            "activePageId": document["pages"][0]["id"],
            "document": document,
            "summary": {"shapeCounts": {}, "semanticEventCount": 0},
        },
    }


class FrameworkPrimitiveTests(unittest.TestCase):
    def test_page_metadata_checks_read_outcome_state(self) -> None:
        log = _log(
            {
                "id": "doc1",
                "schemaVersion": 1,
                "name": "Prototype Spec",
                "pages": [
                    {
                        "id": "page1",
                        "type": "page",
                        "name": "Page 1",
                        "backgroundColor": {"r": 0.1, "g": 0.2, "b": 0.3, "a": 0.42},
                        "backgroundHidden": True,
                        "children": [],
                        "prototypeConnections": [
                            {
                                "id": "conn1",
                                "sourceLayerId": "button1",
                                "destinationFrameId": "frame2",
                                "trigger": "click",
                                "action": "navigate_to",
                                "animation": "instant",
                            }
                        ],
                    }
                ],
            }
        )

        self.assertTrue(DocumentNameEquals("Prototype Spec").run(log).passed)
        self.assertTrue(PageBackgroundOpacityEquals(0.42).run(log).passed)
        self.assertTrue(PageBackgroundHiddenIs(True).run(log).passed)
        self.assertTrue(
            PrototypeConnectionExists(
                source_layer_id="button1",
                destination_frame_id="frame2",
                trigger="click",
                action="navigate_to",
            ).run(log).passed
        )

    def test_center_position_and_line_endpoint_checks_use_visual_geometry(self) -> None:
        log = _log(
            {
                "id": "doc1",
                "schemaVersion": 1,
                "name": "Untitled",
                "pages": [
                    {
                        "id": "page1",
                        "type": "page",
                        "name": "Page 1",
                        "backgroundColor": {"r": 1, "g": 1, "b": 1, "a": 1},
                        "backgroundHidden": False,
                        "children": [
                            {
                                "id": "rect1",
                                "type": "rectangle",
                                "x": -50,
                                "y": -25,
                                "w": 100,
                                "h": 50,
                                "rotation": 0,
                                "scaleX": 1,
                                "scaleY": 1,
                            },
                            {
                                "id": "line1",
                                "type": "line",
                                "x": 10,
                                "y": 20,
                                "w": 100,
                                "h": 1,
                                "rotation": 90,
                                "scaleX": 1,
                                "scaleY": 1,
                                "p1": {"x": 0, "y": 0},
                                "p2": {"x": 100, "y": 0},
                            },
                            {
                                "id": "line2",
                                "type": "line",
                                "x": 60.5,
                                "y": -29.5,
                                "w": 100,
                                "h": 1,
                                "rotation": 0,
                                "scaleX": 1,
                                "scaleY": 1,
                                "p1": {"x": 0, "y": 0},
                                "p2": {"x": 0, "y": 100},
                            },
                        ],
                    }
                ],
            }
        )

        self.assertTrue(LayerCenterPosition("rectangle", x=0, y=0).run(log).passed)
        self.assertTrue(LineLengthEquals("line", math.hypot(100, 0)).run(log).passed)
        self.assertTrue(LineAngleEquals("line", 90).run(log).passed)
        self.assertTrue(LinesShareEndpoint("line", minimum=2).run(log).passed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
