# Per-cell property measurement (Batch D): what OOXML real Word writes for a cell's WIDTH (tcW),
# vertical alignment (vAlign), and margins (tcMar). Pure COM, invisible. PID-safe.
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running. Close Word first."; exit 2 }
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Read-Body($docx) {
  $zip = [System.IO.Compression.ZipFile]::OpenRead($docx)
  try { $e = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' } | Select-Object -First 1
    $sr = New-Object System.IO.StreamReader($e.Open()); try { return $sr.ReadToEnd() } finally { $sr.Dispose() } }
  finally { $zip.Dispose() }
}
$tmp = "C:\tmp\wc-oracle-cellprops"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$out = @()
try {
  $doc = $w.Documents.Add()
  $tbl = $doc.Tables.Add($doc.Range(0,0), 2, 2, 1, 0); $tbl.Style = 'Table Grid'
  $cell = $tbl.Cell(1,1)
  # width 1.5"
  $cell.SetWidth([single](1.5 * 72), 0)   # RulerStyle wdAdjustNone=0; width in points
  # vertical alignment center: wdCellAlignVerticalCenter = 1
  $cell.VerticalAlignment = 1
  # cell margins: top/bottom 0.05", left/right 0.1" (points)
  $cell.TopPadding = [single](0.05 * 72); $cell.BottomPadding = [single](0.05 * 72)
  $cell.LeftPadding = [single](0.1 * 72); $cell.RightPadding = [single](0.1 * 72)
  $f = Join-Path $tmp "cellprops.docx"
  if (Test-Path $f) { Remove-Item -LiteralPath $f -Force }
  $doc.SaveAs2($f, 16); $doc.Close($false)
  $b = Read-Body $f
  # First cell tcPr block
  $tc = if ($b -match '<w:tc>(?:(?!</w:tc>).)*?</w:tcPr>') { $Matches[0] } else { $b.Substring(0, [Math]::Min(600, $b.Length)) }
  $tcW = if ($tc -match '<w:tcW\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $va  = if ($tc -match '<w:vAlign\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $mar = if ($tc -match '<w:tcMar>.*?</w:tcMar>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $out += ("tcW    = " + $tcW)
  $out += ("vAlign = " + $va)
  $out += ("tcMar  = " + $mar)
} catch { $out += ("ERR: " + $_.Exception.Message) }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$out | ForEach-Object { Write-Output $_ }
