# stack_compare.ps1 — stack two screenshots vertically with labels into one comparison PNG.
param(
  [Parameter(Mandatory=$true)][string]$Top,     # e.g. real Word capture
  [Parameter(Mandatory=$true)][string]$Bottom,  # e.g. clone capture
  [string]$TopLabel = 'REAL WORD',
  [string]$BottomLabel = 'CLONE',
  [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$a = [System.Drawing.Image]::FromFile($Top)
$b = [System.Drawing.Image]::FromFile($Bottom)
$w = [Math]::Max($a.Width, $b.Width)
$labelH = 28
$sheet = New-Object System.Drawing.Bitmap($w, ($a.Height + $b.Height + 2 * $labelH + 12))
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.Clear([System.Drawing.Color]::FromArgb(240,240,240))
$font = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Bold)
$y = 0
$g.DrawString($TopLabel, $font, [System.Drawing.Brushes]::DarkRed, 8, ($y + 4)); $y += $labelH
$g.DrawImage($a, 0, $y, $a.Width, $a.Height); $y += $a.Height + 12
$g.DrawString($BottomLabel, $font, [System.Drawing.Brushes]::DarkBlue, 8, ($y + 4)); $y += $labelH
$g.DrawImage($b, 0, $y, $b.Width, $b.Height)
$g.Dispose()
$sheet.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$sheet.Dispose(); $a.Dispose(); $b.Dispose()
Write-Output "saved: $Out"
