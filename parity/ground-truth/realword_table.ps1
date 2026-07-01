# Real-Word Insert Table ground truth — RIBBON-EQUIVALENT (supersedes bare COM Tables.Add).
# Word's Insert Table (grid picker / dialog) applies the "Table Grid" style + the tblLook bitmask + gridCol widths
# + auto tblW — none of which bare COM Tables.Add emits. Reproducing the ribbon = Tables.Add(...,wdWord9TableBehavior,
# wdAutoFitFixed) + $table.Style='Table Grid' (verified in parity/oracle/_explore_tables.ps1: tblStyle=TableGrid,
# tblLook=04A0, gridCol w:w=3116, tblW auto — exactly the ribbon insert). The true grid-picker path is modal-free but
# needs UIA arrow-driving; this COM+style form yields the identical hidden defaults, so it is the faithful ground truth.
param([Parameter(Mandatory = $true)][string]$Out)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Add()
    $rng = $doc.Range(0, 0)
    $tbl = $doc.Tables.Add($rng, 3, 3, 1, 0)   # 3x3; wdWord9TableBehavior=1, wdAutoFitFixed=0
    $tbl.Style = 'Table Grid'                  # the style the ribbon Insert Table applies
    if (Test-Path $Out) { Remove-Item $Out -Force }
    $doc.SaveAs2($Out, 16)
    $doc.Close($false)
    Write-Output "saved: $Out"
} finally {
    $w.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
