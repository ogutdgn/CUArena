# Table oracle exploration (invisible, pure COM + ExecuteMso; no modal dialogs, no SendKeys).
#  (1) Ribbon-equivalent INSERT = Tables.Add + the "Table Grid" style the ribbon applies -> capture the hidden defaults.
#  (2) Confirm the Table Tools Design/Layout ribbon commands are ExecuteMso-able (non-modal) for the deep behaviors.
# PID-safe.
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running. Close Word first."; exit 2 }
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Read-Part($docx, $part) {
  $zip = [System.IO.Compression.ZipFile]::OpenRead($docx)
  try { $e = $zip.Entries | Where-Object { $_.FullName -eq $part } | Select-Object -First 1
    if (-not $e) { return $null }
    $sr = New-Object System.IO.StreamReader($e.Open()); try { return $sr.ReadToEnd() } finally { $sr.Dispose() } }
  finally { $zip.Dispose() }
}
$tmp = "C:\tmp\wc-oracle-feas"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
try {
  # --- (1) Ribbon-equivalent insert: Tables.Add + Table Grid style ---
  $doc = $w.Documents.Add()
  $rng = $doc.Range(0, 0)
  # wdWord9TableBehavior=1, wdAutoFitFixed=0
  $tbl = $doc.Tables.Add($rng, 3, 3, 1, 0)
  $tbl.Style = 'Table Grid'
  $out = "$tmp\rw-table-grid.docx"
  if (Test-Path $out) { Remove-Item $out -Force }
  $doc.SaveAs2($out, 16); $doc.Close($false)
  $body = Read-Part $out 'word/document.xml'
  $sty = Read-Part $out 'word/styles.xml'
  $log += "== INSERT (Tables.Add + Table Grid style) =="
  $log += "  tblStyle=$(if ($body -match 'w:tblStyle[^>]*w:val=\"([^\"]*)\"') { $Matches[1] } else { 'NONE' })"
  $log += "  tblLook=$(if ($body -match '<w:tblLook\b[^>]*/?>') { ($Matches[0] -replace '\s+', ' ') } else { 'NONE' })"
  $log += "  gridCols=$(([regex]::Matches($body, '<w:gridCol\b')).Count)  rows=$(([regex]::Matches($body, '<w:tr\b')).Count)  tcs=$(([regex]::Matches($body, '<w:tc>')).Count)"
  $log += "  firstGridCol=$(if ($body -match '<w:gridCol\b[^>]*/?>') { $Matches[0] } else { 'NONE' })"
  $log += "  tblW=$(if ($body -match '<w:tblW\b[^>]*/?>') { $Matches[0] } else { 'NONE' })"
  $log += "  tblBorders=$([bool]($body -match '<w:tblBorders>'))  tblCellMar=$([bool]($body -match '<w:tblCellMar>'))"
  $log += "  TableGridStyleDefined=$([bool]($sty -match 'w:styleId=\"TableGrid\"'))"

  # --- (2) Are the Table Tools ribbon commands ExecuteMso-able? (validate via GetLabelMso; non-modal apply-toggles) ---
  $log += "== Table Tools idMso validity (GetLabelMso) =="
  $ttMso = @('TableStyleOptionsHeaderRow','TableStyleOptionsBandedRows','TableStyleOptionsTotalRow',
             'TableStyleOptionsFirstColumn','TableStyleOptionsLastColumn','TableStyleOptionsBandedColumns',
             'TableBordersAll','TableBordersOutside','TableBordersInside','TableBordersNone',
             'TableInsertRowAbove','TableInsertRowBelow','TableInsertColumnLeft','TableInsertColumnRight',
             'TableRowsDelete','TableColumnsDelete','TableCellsMerge','TableCellSplit','TableSplit',
             'TableAutoFitContents','TableAutoFitWindow','TableAutoFitFixed','TableColumnsDistribute','TableRowsDistribute',
             'TableAlignmentCenter','TableCellAlignmentCenterCenter','TableTextDirectionCycle','TableSortDialog',
             'TableColumnSelect','TableRowSelect','TableSelect','TableCellSelect','TablePropertiesDialog','ViewGridlines',
             'TableInsertDialog','TableDrawTable','TableEraser','ConvertTextToTable','TableConvertToText','FormulaDialog')
  foreach ($m in $ttMso) {
    $ok = $false; $lbl = ''
    try { $lbl = $w.CommandBars.GetLabelMso($m); $ok = $true } catch {}
    $log += ("  {0} = {1}" -f $m, $(if ($ok) { "OK ('$lbl')" } else { 'INVALID' }))
  }
} catch { $log += "ERR: $($_.Exception.Message)" }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
