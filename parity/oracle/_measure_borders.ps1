# Measure Word's exact tblBorders/tcBorders output for each Borders-dropdown option (whole-table selection).
# Ground truth for the Design-tab Borders group. Invisible, pure COM + ExecuteMso (non-modal). PID-safe.
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
# validate + capture each border option (whole-table selection)
$opts = 'BordersAll','BorderOutside','BorderInside','BorderTop','BorderBottom','BorderLeft','BorderRight',
        'BorderInsideHorizontal','BorderInsideVertical','BorderNone','BorderDiagonalDown','BorderDiagonalUp'
try {
  foreach ($m in $opts) {
    $valid = $false; try { $null = $w.CommandBars.GetLabelMso($m); $valid = $true } catch {}
    if (-not $valid) { $log += "[$m] INVALID idMso"; continue }
    $doc = $w.Documents.Add()
    $tbl = $doc.Tables.Add($doc.Range(0,0), 3, 3, 1, 0); $tbl.Style = 'Table Grid'
    $tbl.Select()
    try { $w.CommandBars.ExecuteMso($m) } catch { $log += "[$m] APPLY ERR: $($_.Exception.Message)" }
    $out = "$tmp\rw-bord-$m.docx"; if (Test-Path $out) { Remove-Item $out -Force }
    $doc.SaveAs2($out, 16); $doc.Close($false)
    $b = Read-Body $out
    $tb = if ($b -match '(?s)<w:tblBorders>.*?</w:tblBorders>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
    $tcb = ([regex]::Matches($b, '<w:tcBorders>')).Count
    # trim to a compact one-liner of side@val@sz
    $sides = [regex]::Matches($tb, '<w:(top|left|bottom|right|insideH|insideV|tl2br|tr2bl)\b[^>]*>') | ForEach-Object {
      $s = $_.Value
      $side = if ($s -match '<w:(\w+)') { $Matches[1] } else { '?' }
      $val = if ($s -match 'w:val="([^"]*)"') { $Matches[1] } else { '' }
      $sz = if ($s -match 'w:sz="([^"]*)"') { $Matches[1] } else { '' }
      "$side=$val/$sz"
    }
    $log += "[$m] tcBorders=$tcb | tblBorders: $($sides -join ' ')"
  }
} catch { $log += "ERR: $($_.Exception.Message)" }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
