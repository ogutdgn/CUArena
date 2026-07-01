# Insert-Table AutoFit behavior measurement (Batch A creation): what OOXML real Word writes for each
# of the Insert Table dialog's AutoFit modes — Fixed column width / AutoFit to contents / AutoFit to window.
# Captures tblW, tblLayout, gridCol. Pure COM, invisible. PID-safe.
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
$tmp = "C:\tmp\wc-oracle-autofit"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$out = @()
try {
  # wdAutoFitFixed=0, wdAutoFitContent=1, wdAutoFitWindow=2
  foreach ($pair in @(@('fixed',0), @('contents',1), @('window',2))) {
    $mode = $pair[0]; $af = [int]$pair[1]
    $doc = $w.Documents.Add()
    $tbl = $doc.Tables.Add($doc.Range(0,0), 2, 3, 1, $af)
    $tbl.Style = 'Table Grid'
    $f = Join-Path $tmp ("af-" + $mode + ".docx")
    if (Test-Path $f) { Remove-Item -LiteralPath $f -Force }
    $doc.SaveAs2($f, 16); $doc.Close($false)
    $b = Read-Body $f
    $tblW = if ($b -match '<w:tblW\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
    $lay  = if ($b -match '<w:tblLayout\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
    $cols = ([regex]::Matches($b, '<w:gridCol\b[^>]*/?>') | ForEach-Object { ($_.Value -replace '\s+',' ') }) -join ' '
    $out += ("[" + $mode + "] tblW=" + $tblW + " | tblLayout=" + $lay)
    $out += ("        gridCols=" + $cols)
  }
} catch { $out += ("ERR: " + $_.Exception.Message) }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$out | ForEach-Object { Write-Output $_ }
