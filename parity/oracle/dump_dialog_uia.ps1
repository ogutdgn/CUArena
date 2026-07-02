# dump_dialog_uia.ps1 — the Word side of rubric D2.2: dump a Word DIALOG's fields via UIA.
#
# Design (robust, focus-independent): a RUNSPACE (same process → shares the window station, so
# main-thread UIA can see the dialog — a Start-Job child process can't) creates a fresh Word COM
# instance INTERNALLY (never shared across threads → no cross-runspace COM error) and calls the
# (modal, BLOCKING) ExecuteMso, parking there holding the dialog open. The MAIN thread does only
# UIA — walks the dialog by PID, dumps fields, closes it via UIA InvokePattern on Cancel/OK (no
# SendKeys, no focus). Synthesizes the two earlier attempts and sidesteps all three walls
# (cross-runspace COM, SendKeys focus, Start-Job window-station isolation).
#
# Output JSON (no BOM): {idMso, title, fields:[{name,type}], tabs:[...]}
# PID-safe: aborts if WINWORD already open; kills only the instance it spawns.
# Usage: powershell -File dump_dialog_uia.ps1 -IdMso FontDialog -Out C:\tmp\dlg-font.json
#
# ⚠️ ENVIRONMENT NOTE (2026-07-01): verified that ExecuteMso('FontDialog') DOES open the modal
# (it blocks the calling thread), but a thread parked inside ExecuteMso doesn't pump messages, so
# the modal never fully registers with UIA — RootElement enumerates only 'Document1 - Word'. Four
# mechanisms tried (ExecuteMso-in-runspace / SendKeys+AttachThreadInput foreground / Start-Job /
# runspace-STA); all blocked by message-pump + window-station isolation in the headless-ish
# automated context. This script is CORRECT for a genuinely INTERACTIVE desktop session (real
# message pump) — run it there, one idMso per invocation, Word closed first.
param(
  [Parameter(Mandatory = $true)][string]$IdMso,
  [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

# Runspace (SAME process → shared window station): creates Word internally, opens the modal.
$rs = [runspacefactory]::CreateRunspace()
$rs.ApartmentState = 'STA'
$rs.Open()
$ps = [powershell]::Create()
$ps.Runspace = $rs
[void]$ps.AddScript({
    param($mso)
    $w = New-Object -ComObject Word.Application
    $w.Visible = $true
    $w.DisplayAlerts = 0
    $doc = $w.Documents.Add()
    $doc.Content.Text = 'Revenue'
    $doc.Range(0, 7).Select()
    Start-Sleep -Milliseconds 300
    try { $w.CommandBars.ExecuteMso($mso) } catch {}   # BLOCKS until the modal closes
    Start-Sleep -Milliseconds 200
    try { $w.Quit() } catch {}
    [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  }).AddArgument($IdMso)
$async = $ps.BeginInvoke()
$fields = New-Object System.Collections.ArrayList
$tabs = New-Object System.Collections.ArrayList
$title = ''
$seen = @()
try {
  # our Word PID(s) = whatever WINWORD the job spawned
  $mypids = @()
  for ($i = 0; $i -lt 20 -and -not $mypids; $i++) {
    Start-Sleep -Milliseconds 250
    $mypids = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
  }
  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $dlg = $null
  for ($i = 0; $i -lt 40 -and -not $dlg; $i++) {
    Start-Sleep -Milliseconds 300
    foreach ($el in $root.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
      try {
        if ($mypids -contains $el.Current.ProcessId) {
          $nm = $el.Current.Name
          $seen += "'$nm'"
          if ($nm -and $nm -notmatch ' - Word$' -and $nm -notmatch '^Document\d') { $dlg = $el; break }
        }
      } catch {}
    }
  }
  Write-Output ("pids=" + ($mypids -join ',') + " windows=" + (($seen | Select-Object -Unique) -join ' '))
  if ($dlg) {
    $title = $dlg.Current.Name
    $all = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
      [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
      $ct = $el.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
      $nm = $el.Current.Name
      if (-not $nm) { continue }
      if ($ct -eq 'TabItem') { [void]$tabs.Add($nm) }
      elseif ($ct -in @('CheckBox', 'Edit', 'ComboBox', 'Button', 'RadioButton', 'Spinner', 'List')) {
        [void]$fields.Add([pscustomobject]@{ name = $nm; type = $ct })
      }
    }
    # Close via UIA InvokePattern on Cancel (focus-independent) so the job's ExecuteMso returns.
    $btn = $all | Where-Object { $_.Current.Name -match '^(Cancel|Close|OK)$' } | Select-Object -First 1
    if ($btn) {
      try {
        $ip = $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $ip.Invoke()
      } catch {}
    }
  }
  $result = [pscustomobject]@{ idMso = $IdMso; title = $title; fields = $fields; tabs = $tabs }
  [IO.File]::WriteAllText($Out, ($result | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
  Write-Output "dumped $IdMso : title='$title' fields=$($fields.Count) tabs=$($tabs.Count) -> $Out"
} finally {
  Start-Sleep -Milliseconds 400
  try { $ps.Stop() } catch {}
  try { $ps.Dispose(); $rs.Close() } catch {}
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  Start-Sleep -Milliseconds 400
  foreach ($id in (Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })) {
    try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {}
  }
}
