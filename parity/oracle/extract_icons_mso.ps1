# extract_icons_mso.ps1 — pull REAL Word ribbon icons via CommandBars.GetImageMso (D5.5 ground truth).
#
# Saves each icon as an alpha-preserving PNG (the raw HBITMAP is 32bpp ARGB; a plain
# Image.FromHbitmap drops the alpha channel, so we re-wrap the locked bits as Format32bppArgb).
# Also writes a contact-sheet PNG (icons scaled 4x, nearest-neighbor, labeled) for eyeballing.
#
# PID-safe: aborts if WINWORD is already open; kills only the instance it spawns.
# Usage: powershell -File extract_icons_mso.ps1 -Ids 'Bold,Italic,TableDrawTable' -Size 32 -OutDir C:\tmp\mso-icons
param(
  [string]$Ids = 'Bold,Italic,Underline,Copy,Paste,FormatPainter,FontColorPicker,TextHighlightColorPicker,TableDrawTable,TableEraser,MergeCells,TableRowsInsertAboveWord',
  [int]$Size = 32,
  [string]$OutDir = 'C:\tmp\mso-icons'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force $OutDir | Out-Null }

$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$saved = @()
try {
  $cb = $w.CommandBars
  foreach ($id in ($Ids -split ',' | Where-Object { $_.Trim() })) {
    $id = $id.Trim()
    try {
      $pic = $cb.GetImageMso($id, $Size, $Size)
      $bmp = [System.Drawing.Bitmap]::FromHbitmap($pic.Handle)
      $rect = New-Object System.Drawing.Rectangle(0, 0, $bmp.Width, $bmp.Height)
      $data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
      $argb = New-Object System.Drawing.Bitmap($bmp.Width, $bmp.Height, $data.Stride, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb, $data.Scan0)
      $path = Join-Path $OutDir "$id.png"
      $argb.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
      $bmp.UnlockBits($data); $argb.Dispose(); $bmp.Dispose()
      $saved += $id
      Write-Output "OK  $id -> $path"
    } catch { Write-Output "ERR $id : $($_.Exception.Message)" }
  }

  # Contact sheet: 4x nearest-neighbor scale + label per icon, white background.
  if ($saved.Count -gt 0) {
    $cell = ($Size * 4) + 8; $labelH = 16; $cols = [Math]::Min(6, $saved.Count)
    $rows = [Math]::Ceiling($saved.Count / $cols)
    $sheet = New-Object System.Drawing.Bitmap(($cols * ($cell + 60)), ($rows * ($cell + $labelH + 10)))
    $g = [System.Drawing.Graphics]::FromImage($sheet)
    $g.Clear([System.Drawing.Color]::White)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $font = New-Object System.Drawing.Font('Segoe UI', 7)
    for ($i = 0; $i -lt $saved.Count; $i++) {
      $ic = [System.Drawing.Image]::FromFile((Join-Path $OutDir "$($saved[$i]).png"))
      $x = ($i % $cols) * ($cell + 60) + 4; $y = [Math]::Floor($i / $cols) * ($cell + $labelH + 10) + 4
      $g.DrawImage($ic, $x, $y, $Size * 4, $Size * 4)
      $g.DrawString($saved[$i], $font, [System.Drawing.Brushes]::Black, $x, ($y + $Size * 4 + 2))
      $ic.Dispose()
    }
    $g.Dispose()
    $sheetPath = Join-Path $OutDir '_contact-sheet.png'
    $sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $sheet.Dispose()
    Write-Output "sheet: $sheetPath"
  }
  Write-Output "done: $($saved.Count) icons"
} finally {
  $w.Quit()
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
