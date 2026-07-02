# Real-Word bullets ground truth — RIBBON oracle (real-ribbon ground truth; supersedes the COM version).
# Drives the ACTUAL Bullets gallery button via CommandBars.ExecuteMso('BulletsGalleryWord') — which writes a
# MULTILEVEL (hybridMultilevel, 9-level) abstractNum, exactly like the clone. This REPLACES the old COM
# ListFormat.ApplyBulletDefault() ground truth, which wrote a single-level abstractNum (a COM-scripting artifact,
# now PROVEN — see parity/oracle/_feasibility_executemso.ps1). Same 'Revenue' selection as the clone bullets probe.
param([Parameter(Mandatory = $true)][string]$Out)
& "$PSScriptRoot\..\oracle\ribbon_oracle.ps1" -Out $Out -Text 'Revenue' -Mso 'BulletsGalleryWord'
