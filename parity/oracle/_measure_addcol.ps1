# Does real Word keep a table within the page when columns are added? Insert a 3-col table,
# add 10 columns, save, and sum the gridCol widths vs the page text width. PID-safe, invisible.
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
$tmp = "C:\tmp\wc-oracle-addcol"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$out = @()
try {
  $doc = $w.Documents.Add()
  # page text width (twips) = pageWidth - left - right margins
  $ps = $doc.PageSetup
  $textW = [int]([math]::Round(($ps.PageWidth - $ps.LeftMargin - $ps.RightMargin) * 20))
  $out += ("pageTextWidthTwips=" + $textW)
  $tbl = $doc.Tables.Add($doc.Range(0,0), 2, 3, 1, 0); $tbl.Style = 'Table Grid'
  # sum gridCol at 3 cols
  $f0 = Join-Path $tmp "c3.docx"; if (Test-Path $f0) { Remove-Item $f0 -Force }
  $doc.SaveAs2($f0, 16)
  $b0 = Read-Body $f0
  $g0 = ([regex]::Matches($b0, '<w:gridCol\b[^>]*w:w="(\d+)"') | ForEach-Object { [int]$_.Groups[1].Value })
  $out += ("cols=3 gridColSum=" + ($g0 | Measure-Object -Sum).Sum + " count=" + $g0.Count)
  # add 10 columns (to the right end): select last cell of row 1, Columns.Add adds to the LEFT of selection,
  # so repeatedly add at the end via the table's Columns.
  for ($i = 0; $i -lt 10; $i++) { $tbl.Columns.Add() | Out-Null }
  $f1 = Join-Path $tmp "c13.docx"; if (Test-Path $f1) { Remove-Item $f1 -Force }
  $doc.SaveAs2($f1, 16); $doc.Close($false)
  $b1 = Read-Body $f1
  $g1 = ([regex]::Matches($b1, '<w:gridCol\b[^>]*w:w="(\d+)"') | ForEach-Object { [int]$_.Groups[1].Value })
  $tblW = if ($b1 -match '<w:tblW\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $lay = if ($b1 -match '<w:tblLayout\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $out += ("cols=" + $g1.Count + " gridColSum=" + ($g1 | Measure-Object -Sum).Sum)
  $out += ("tblW=" + $tblW + " tblLayout=" + $lay)
  $out += ("fitsPage=" + (($g1 | Measure-Object -Sum).Sum -le $textW + 40))
} catch { $out += ("ERR: " + $_.Exception.Message) }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$out | ForEach-Object { Write-Output $_ }
