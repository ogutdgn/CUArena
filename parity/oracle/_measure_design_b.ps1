# Group B (Table Design) measurement: validate the idMso + capture the ribbon output of each Design command applied
# to a real inserted table (Tables.Add + Table Grid). Invisible, pure COM + ExecuteMso (non-modal toggles). PID-safe.
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
$tmp = "C:\tmp\wc-oracle-feas"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
# (1) validate the group-B idMso
$msos = 'TableStyleHeaderRowWord','TableStyleTotalRowWord','TableStyleBandedRowsWord','TableStyleFirstColumnWord',
        'TableStyleLastColumnWord','TableStyleBandedColumnsWord','TableStylesGalleryWord','ShadingColorPicker',
        'BordersAll','BorderOutside','BorderInside','BorderTop','BorderBottom','BorderLeft','BorderRight','BorderNone',
        'BorderDiagonalDown','BorderDiagonalUp','BorderStylesGallery','BorderColorPicker','TableShadingColorPicker',
        'ShadingGalleryWord','TableColumnsDistribute','TableCellAlignTopLeft','TableTextDirection','TableSortDialog','TableFormula'
try {
  $log += "== idMso validity =="
  foreach ($m in $msos) { $ok=$false; try { $null=$w.CommandBars.GetLabelMso($m); $ok=$true } catch {}; if ($ok) { $log += "  $m = OK" } }

  # (2) measure a few: insert a table, select it, apply the Design command, capture
  function ApplyOnTable($mso, $out) {
    $doc = $w.Documents.Add()
    $tbl = $doc.Tables.Add($doc.Range(0,0), 3, 3, 1, 0); $tbl.Style = 'Table Grid'
    $tbl.Select()
    $applied = $false
    try { $w.CommandBars.ExecuteMso($mso); $applied = $true } catch { $log += "  APPLY $mso ERR: $($_.Exception.Message)" }
    if (Test-Path $out) { Remove-Item $out -Force }
    $doc.SaveAs2($out, 16); $doc.Close($false)
    return $applied
  }
  $log += "== sample captures =="
  foreach ($m in @('TableStyleHeaderRowWord','TableStyleBandedRowsWord','BordersAll','BorderNone')) {
    $out = "$tmp\rw-design-$m.docx"
    if (ApplyOnTable $m $out) {
      $b = Read-Body $out
      $tl = if ($b -match '<w:tblLook\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
      $cnf = ([regex]::Matches($b, '<w:cnfStyle\b')).Count
      $tb = [bool]($b -match '<w:tblBorders>'); $tcb = ([regex]::Matches($b, '<w:tcBorders>')).Count
      $log += "  [$m] tblLook=$tl | cnfStyle=$cnf | tblBorders=$tb | tcBorders=$tcb"
    }
  }
} catch { $log += "ERR: $($_.Exception.Message)" }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
