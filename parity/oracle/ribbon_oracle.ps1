# Ribbon oracle — REAL-ribbon ground truth for the parity pipeline.
#
# Drives the ACTUAL ribbon command(s) via CommandBars.ExecuteMso (the button's real code path, NOT COM scripting)
# on a prepared selection, then saves the .docx so the differ can compare document.xml / numbering.xml / styles.xml.
# This is the ground truth COM scripting could not give — e.g. the Bullets gallery writes a MULTILEVEL abstractNum
# (matching the clone) where COM ListFormat.ApplyBulletDefault writes a single-level one.
#
# PID-safe: aborts if any WINWORD is already open; kills ONLY the instance it spawns.
#
# Params:
#   -Out   <path>           the .docx to write
#   -Text  <string>         body text to type (default 'Revenue')
#   -SelStart <int>         selection start (default 0)
#   -SelLen <int>           selection length (default = whole Text). -1 = caret at end (no selection).
#   -Mso   <string>         comma-separated idMso list executed IN ORDER on the selection (e.g. 'Bold' or 'Underline,Bold')
#   -PreMso <string>        comma-separated idMso executed BEFORE re-selecting (rare; e.g. gallery setup)
param(
  [Parameter(Mandatory = $true)][string]$Out,
  [string]$Text = 'Revenue',
  [int]$SelStart = 0,
  [int]$SelLen = -2,          # -2 sentinel => whole text
  [string]$Mso = '',
  [string]$PreMso = ''
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }

$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
try {
  $doc = $w.Documents.Add()
  if ($Text.Length -gt 0) { $doc.Content.Text = $Text }
  $len = if ($SelLen -eq -2) { $Text.Length } else { $SelLen }

  foreach ($m in ($PreMso -split ',' | Where-Object { $_.Trim() })) {
    try { $w.CommandBars.ExecuteMso($m.Trim()); $log += "pre:$($m.Trim())=OK" } catch { $log += "pre:$($m.Trim())=ERR:$($_.Exception.Message)" }
  }

  # (Re)establish the selection right before the action so ExecuteMso targets it.
  if ($len -eq -1) { $doc.Range($Text.Length, $Text.Length).Select() }
  else { $doc.Range($SelStart, $SelStart + $len).Select() }

  foreach ($m in ($Mso -split ',' | Where-Object { $_.Trim() })) {
    $mm = $m.Trim()
    $en = $true
    try { $en = $w.CommandBars.GetEnabledMso($mm) } catch {}
    try { $w.CommandBars.ExecuteMso($mm); $log += "$mm=OK(enabled=$en)" } catch { $log += "$mm=ERR:$($_.Exception.Message)" }
  }

  if (Test-Path $Out) { Remove-Item $Out -Force }
  $doc.SaveAs2($Out, 16)
  $doc.Close($false)
  Write-Output "saved: $Out"
  $log | ForEach-Object { Write-Output "  $_" }
} finally {
  $w.Quit()
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
