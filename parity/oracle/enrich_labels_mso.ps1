# enrich_labels_mso.ps1 — attach REAL Word display labels + enablement to the idMso inventory.
#
# Reads a plain-text list of idMso names (one per line), asks the installed Word (the locked
# parity build) for CommandBars.GetLabelMso / GetEnabledMso on each, and writes a TSV:
#   idMso <TAB> label <TAB> enabled
# Lines where the call errors get label='' / enabled=''. A blank document is opened first so
# enablement reflects the normal document-open context.
#
# PID-safe: aborts if any WINWORD is already open; kills ONLY the instance it spawns.
# Metadata-only COM calls (no ExecuteMso, no SaveAs) — the calls that have hung before are not used.
#
# Usage: powershell -File parity/oracle/enrich_labels_mso.ps1 -List <idmso.txt> -Out <labels.tsv>
param(
  [Parameter(Mandatory = $true)][string]$List,
  [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }

$ids = Get-Content $List | Where-Object { $_.Trim() }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$sw = New-Object IO.StreamWriter($Out, $false, (New-Object Text.UTF8Encoding($false)))
$done = 0
try {
  $doc = $w.Documents.Add()   # enablement in a document-open context
  $cb = $w.CommandBars
  foreach ($id in $ids) {
    $id = $id.Trim()
    $label = ''
    $enabled = ''
    try { $label = $cb.GetLabelMso($id) } catch {}
    try { $enabled = $cb.GetEnabledMso($id) } catch {}
    $label = ($label -replace "`t", ' ') -replace "`r?`n", ' '
    $sw.WriteLine("$id`t$label`t$enabled")
    $done++
    if ($done % 500 -eq 0) { $sw.Flush(); Write-Output "  ...$done/$($ids.Count)" }
  }
  $doc.Close($false)
  Write-Output "done: $done ids -> $Out"
} finally {
  $sw.Close()
  $w.Quit()
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
