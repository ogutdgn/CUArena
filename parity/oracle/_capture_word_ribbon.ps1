# Capture REAL Word's ribbon for a given contextual tab, to a PNG (for pixel comparison against the clone).
# Launches a VISIBLE Word, inserts a table, selects it, uses UI Automation to click the requested ribbon
# tab, then PrintWindow-captures the Word window. PID-safe: only closes the Word it spawned.
# Usage: powershell -File _capture_word_ribbon.ps1 -Tab 'Table Design' -Out C:\tmp\word-design.png
param(
  [string]$Tab = 'Table Design',
  [string]$Out = 'C:\tmp\word-ribbon.png',
  [string]$Style = '',       # optional: apply this table style to the base table (level-4 doc shots)
  [string]$Mso = '',         # optional: ExecuteMso AFTER tab activation (drops a gallery/menu for level-2 shots)
  [switch]$PickLast          # tab-name collision (contextual 'Layout' vs the standard Layout tab): take the LAST match
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class Win32Cap {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public static void Capture(IntPtr hwnd, string path) {
    RECT r; GetWindowRect(hwnd, out r);
    int w = r.Right - r.Left, h = r.Bottom - r.Top;
    if (w < 1 || h < 1) { w = 1440; h = 900; }
    Bitmap bmp = new Bitmap(w, h);
    using (Graphics g = Graphics.FromImage(bmp)) {
      IntPtr hdc = g.GetHdc();
      PrintWindow(hwnd, hdc, 2); // PW_RENDERFULLCONTENT
      g.ReleaseHdc(hdc);
    }
    bmp.Save(path, System.Drawing.Imaging.ImageFormat.Png);
  }
}
"@ -ReferencedAssemblies System.Drawing
$w = New-Object -ComObject Word.Application
$w.Visible = $true
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$wordPid = if ($spawned.Count -gt 0) { $spawned[0] } else { $null }
try {
  $doc = $w.Documents.Add()
  $tbl = $doc.Tables.Add($doc.Range(0,0), 3, 3, 1, 0); $tbl.Style = 'Table Grid'
  if ($Style) { $tbl.Style = $Style }
  $tbl.Cell(1,1).Select()
  $w.Selection.Collapse(1)
  try { $w.ActiveWindow.View.Zoom.Percentage = 100 } catch {}
  $w.WindowState = 1  # wdWindowStateMaximize
  Start-Sleep -Milliseconds 1200
  # UIA: find the Word window by pid, then click the requested ribbon tab (SelectionItem pattern).
  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $pidCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, [int]$wordPid)
  $win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $pidCond)
  $activated = $false
  if ($win) {
    $nameCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Tab)
    $tabEl = $null
    if ($PickLast) {
      # contextual 'Layout' shares its name with the standard Layout tab; the contextual one
      # is LAST in tab order — take the last TabItem match.
      $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $nameCond)
      for ($i = $all.Count - 1; $i -ge 0; $i--) {
        $cand = $all.Item($i)
        if ($cand.Current.ControlType -eq [System.Windows.Automation.ControlType]::TabItem) { $tabEl = $cand; break }
      }
      if (-not $tabEl -and $all.Count -gt 0) { $tabEl = $all.Item($all.Count - 1) }
    } else {
      $tabEl = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $nameCond)
    }
    if ($tabEl) {
      try {
        $si = $tabEl.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
        $si.Select(); $activated = $true
      } catch {
        try { $inv = $tabEl.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); $inv.Invoke(); $activated = $true } catch {}
      }
    }
  }
  Start-Sleep -Milliseconds 1000
  if ($Mso) {
    # Level-2 shots: drop a gallery/menu. ExecuteMso on a gallery only OPENS it (proven in the
    # worklist feasibility runs) — exactly what a menu-open screenshot needs.
    try { $w.CommandBars.ExecuteMso($Mso); Start-Sleep -Milliseconds 1200 } catch { Write-Output ("MSO '" + $Mso + "' ERR: " + $_.Exception.Message) }
  }
  $hwnd = (Get-Process -Id $wordPid).MainWindowHandle
  [Win32Cap]::SetForegroundWindow($hwnd) | Out-Null
  Start-Sleep -Milliseconds 400
  if (Test-Path $Out) { Remove-Item -LiteralPath $Out -Force }
  [Win32Cap]::Capture($hwnd, $Out)
  Write-Output ("TAB='" + $Tab + "' activated=" + $activated + " hwnd=" + $hwnd + " -> " + $Out)
} finally {
  try { $doc.Saved = $true } catch {}
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
