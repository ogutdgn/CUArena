# Real-Word numbering ground truth — RIBBON oracle (real-ribbon ground truth; supersedes the COM version).
# Drives the ACTUAL Numbering gallery button via CommandBars.ExecuteMso('NumberingGalleryWord') — the ribbon's
# real multilevel list template — replacing the old COM ListFormat.ApplyNumberDefault() single-level artifact.
# Same 'Revenue' selection as the clone numbering probe.
param([Parameter(Mandatory = $true)][string]$Out)
& "$PSScriptRoot\..\oracle\ribbon_oracle.ps1" -Out $Out -Text 'Revenue' -Mso 'NumberingGalleryWord'
