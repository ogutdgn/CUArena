# capture_enabled_states.ps1 — the STATE matrix's Word side (rubric D2.4).
#
# Drives real Word through canonical CONTEXTS and asks GetEnabledMso for every idMso in each:
#   ctx1  blank doc, caret in text (baseline editing context)
#   ctx2  text selected
#   ctx3  caret inside a table
# Output TSV: idMso <TAB> ctx1 <TAB> ctx2 <TAB> ctx3   (True/False/'' on error)
#
# Metadata-only COM (GetEnabledMso proven hang-free on this build). PID-safe: aborts if WINWORD
# is open; kills only what it spawns.
# Usage: powershell -File capture_enabled_states.ps1 -List _idmso_list.txt -Out _enabled_states.tsv
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
$rows = @{}
foreach ($id in $ids) { $rows[$id.Trim()] = @('', '', '') }

function Sweep([object]$cb, [hashtable]$rows, [int]$slot) {
  foreach ($id in @($rows.Keys)) {
    try { $rows[$id][$slot] = [string]$cb.GetEnabledMso($id) } catch {}
  }
}

try {
  $doc = $w.Documents.Add()
  $cb = $w.CommandBars

  # ctx1 — caret in text
  $doc.Content.Text = 'Revenue increased in the second quarter.'
  $doc.Range(3, 3).Select()
  Sweep $cb $rows 0
  Write-Output 'ctx1 done'

  # ctx2 — text selected
  $doc.Range(0, 7).Select()
  Sweep $cb $rows 1
  Write-Output 'ctx2 done'

  # ctx3 — caret inside a table
  $end = $doc.Content.End - 1
  $tbl = $doc.Tables.Add($doc.Range($end, $end), 2, 2)
  $tbl.Cell(1, 1).Range.Select()
  $w.Selection.Collapse(1) | Out-Null
  Sweep $cb $rows 2
  Write-Output 'ctx3 done'

  $sw = New-Object IO.StreamWriter($Out, $false, (New-Object Text.UTF8Encoding($false)))
  foreach ($id in ($rows.Keys | Sort-Object)) { $sw.WriteLine(($id + "`t" + ($rows[$id] -join "`t"))) }
  $sw.Close()
  Write-Output "wrote $($rows.Count) ids -> $Out"
} finally {
  $w.Quit()
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
