# dump_dialog_uia.ps1 — the Word side of rubric D2.2: dump a Word DIALOG's fields via UIA.
#
# Design: main-thread COM (visible, maximized, foreground). Open the dialog with SendKeys (NOT
# ExecuteMso) so the CALLING thread is NOT blocked — Word's own UI thread pumps the modal, so our
# main thread stays free to UIA-walk it. The earlier ExecuteMso attempts blocked the caller (no
# message pump → the modal never registered with UIA). Requires a real interactive desktop and no
# user input during the run (foreground focus must hold). Close via UIA InvokePattern (Cancel/OK).
#
# Output JSON (no BOM): {key, title, fields:[{name,type}], tabs:[...]}
# PID-safe: aborts if WINWORD already open; kills only what it spawns.
# Usage: powershell -File dump_dialog_uia.ps1 -Key font -Out C:\tmp\dlg-font.json
param(
  [Parameter(Mandatory = $true)][string]$Key,
  [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = 'Stop'
# logical key -> open accelerator (SendKeys). Keys match dialog-fields-probe.js / dialog_verify.
$ACCEL = @{
  font          = '^d'          # Ctrl+D
  paragraph     = '%hpg'        # Alt,H,P,G
  findadv       = '^h'          # Replace (has the Find tab)
  wordcount     = '%rw'         # Review > Word Count
  paste_special = '%hvs'        # Home > Paste > Paste Special
  insert_table  = '%nti'        # Insert > Table > Insert Table
  page_setup    = '%psp'        # Layout > Page Setup launcher
}
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
if (-not $ACCEL.ContainsKey($Key)) { Write-Error "unknown -Key '$Key'. Known: $($ACCEL.Keys -join ', ')"; exit 2 }
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Fg {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  public static void Force(IntPtr h) {
    ShowWindow(h, 9); IntPtr fg = GetForegroundWindow(); uint pid;
    uint fgT = GetWindowThreadProcessId(fg, out pid); uint myT = GetCurrentThreadId();
    AttachThreadInput(fgT, myT, true); BringWindowToTop(h); SetForegroundWindow(h);
    AttachThreadInput(fgT, myT, false);
  }
}
"@

$w = New-Object -ComObject Word.Application
$w.Visible = $true
$w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$fields = New-Object System.Collections.ArrayList
$tabs = New-Object System.Collections.ArrayList
$title = ''; $seen = @()
try {
  $doc = $w.Documents.Add()
  $doc.Content.Text = 'Revenue'
  try { $w.ActiveWindow.WindowState = 1 } catch {}   # maximize
  $doc.Range(0, 7).Select()
  $w.Activate()
  Start-Sleep -Milliseconds 800
  $hwnd = [intptr]$w.ActiveWindow.Hwnd
  [Fg]::Force($hwnd)
  Start-Sleep -Milliseconds 500
  $fgOk = ([Fg]::GetForegroundWindow() -eq $hwnd)
  # nudge a harmless key so the document surface has keyboard focus, then the accelerator
  [System.Windows.Forms.SendKeys]::SendWait('{RIGHT}')
  Start-Sleep -Milliseconds 200
  [System.Windows.Forms.SendKeys]::SendWait($ACCEL[$Key])
  Write-Output "foreground=$fgOk key=$($ACCEL[$Key])"

  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $dlg = $null
  for ($i = 0; $i -lt 30 -and -not $dlg; $i++) {
    Start-Sleep -Milliseconds 300
    foreach ($el in $root.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
      try {
        if ($spawned -contains $el.Current.ProcessId) {
          $nm = $el.Current.Name; $seen += "'$nm'"
          if ($nm -and $nm -notmatch ' - Word$' -and $nm -notmatch '^Document\d') { $dlg = $el; break }
        }
      } catch {}
    }
  }
  Write-Output ("windows=" + (($seen | Select-Object -Unique) -join ' '))
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
    $btn = $all | Where-Object { $_.Current.Name -match '^(Cancel|Close|OK)$' } | Select-Object -First 1
    if ($btn) { try { $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() } catch {} }
    Start-Sleep -Milliseconds 200
    try { [System.Windows.Forms.SendKeys]::SendWait('{ESC}') } catch {}
  }
  $result = [pscustomobject]@{ key = $Key; title = $title; fields = $fields; tabs = $tabs }
  [IO.File]::WriteAllText($Out, ($result | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
  Write-Output "dumped $Key : title='$title' fields=$($fields.Count) tabs=$($tabs.Count) -> $Out"
} finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  Start-Sleep -Milliseconds 400
  foreach ($id in (Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })) {
    try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {}
  }
}
