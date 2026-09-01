# Priority justification — word-home-insert run

**Why these are the top layer.** The P0 set — Pictures, Bold, Font, Font Size — and the P1 set
just beneath it (Paste, Copy, Cut, Italic, Underline, Font Color, Align Left/Center, Find,
Table, Page Break) are exactly the commands every Word user touches constantly: Microsoft's own
CEIP telemetry puts Paste, Copy and Bold in the top five of ALL Word command use (~32%
combined), fixes Change Font Size at #11, and shows the usage curve flattening sharply after
the top ~10. On the Insert side, no command reaches the telemetry top-10, so the band tops out
at P1/P2 — led by Tables and Pictures (browser Word's only fully-supported insert-content
categories, 20–25% and 15–20% MOS Associate exam domains, and the largest tutorial
ecosystems) and Header/Footer/Page Number (the only document-furniture entry in the OWL
command-logging top-20; 380 SuperUser matches for page numbers, the highest Insert probe).
The two ribbon dialog launchers (Font, Paragraph) ride into P2 on connectivity — they are the
consolidation hubs of the entire formatting graph (degree 14 and 12, the two highest).

**Mechanics.** Signals: connectivity (deterministic degree centrality over the measured
affects/uses graph), real-world usage (evidence-cited web research: CEIP telemetry, MOS exam
weights, curricula, SuperUser same-pattern volumes — every score carries claim + source URLs
in `signals/usage.json`), audience breadth (fixed lookup). Weights 0.30/0.40/0.30, boundaries
P0≥0.78, P1≥0.66, P2≥0.52, P3≥0.36 — all recorded in `ranking.json`/`layers.json`. Boundary
features (Voice, Editor, Acrobat, Add-ins, eSignature) are floored to P4 by policy: we will
not spend depth budget on cloud/add-in surfaces we deliberately do not press.

**Sanity check.** Nothing niche sits above P2; nothing an everyday user touches sits below P3.
Layer counts: P0=4, P1=15, P2=17, P3=22, P4=35 (93 nodes).
