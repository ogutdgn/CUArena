"""
Task 07 — Layered mountain range (IN SCOPE).

Two pen-tool paths in different gray shades — closer mountain in front of farther one.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersOverlap, LayerAspectRatioGreaterThan
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors, AllSolidColorsNearGray
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_07_mountain_range",
    description="Two overlapping pen-tool mountain paths in different gray shades.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("vector", equals=2),                                                     # 0 ★ prompt: "two ... pen-tool paths"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayersOverlap(type_a="vector", type_b="vector"),                                    # 0 ★ prompt: "overlapping pen-tool paths"
            LayerAspectRatioGreaterThan(layer_type="vector", ratio=1.8, axis="horizontal"),     # 1 ★ prompt: "mountain silhouette" (wide)
        ], weight=0.30, critical=[0, 1]),

        ColorRubric([
            FillTypeIs("vector", kind="solid"),                                                 # 0 ★ prompt: "Apply dark gray fill"
            DistinctSolidColors(minimum=2, tolerance=0.12),                                     # 1 ★ prompt: "different shades"
            AllSolidColorsNearGray(layer_type="vector", tolerance=0.14),                        # 2 ★ prompt: "gray ... lighter gray"
        ], weight=0.25, critical=[0, 1, 2]),

        StructureRubric([
            LayerInsideFrame("vector"),                                                         # 0 ★ prompt: "Create a 1000x400 frame"
        ], weight=0.15, critical=[0]),

        EventRubric([
            ToolUsed("pen"),                                                                    # 0 ★ prompt: "Use the Pen tool"
            EventTypeCountAtLeast("create_vector_with_pen", minimum=2),                         # 1 ★ mock emits this name (not "create_vector")
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
