# Feasibility probe: drive the REAL Insert Table ribbon dialog to completion via ExecuteMso (open) + SendKeys
# (fill columns/rows + OK). This is the actual ribbon dialog interaction (NOT COM Tables.Add scripting), so its
# output carries whatever hidden defaults the ribbon applies (Table Grid style, tblLook, gridCol, tcMar).
# PID-safe; Word VISIBLE (required to receive keystrokes). Kills only the spawned instance.
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
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
$w.Visible = $true
$w.DisplayAlerts = 0
$wsh = New-Object -ComObject WScript.Shell
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
try {
  $doc = $w.Documents.Add()
  $doc.Content.Text = ''
  $w.Activate()
  Start-Sleep -Milliseconds 600
  try { $wsh.AppActivate($w.Caption) | Out-Null } catch {}
  Start-Sleep -Milliseconds 300

  $w.CommandBars.ExecuteMso('TableInsertDialog')
  Start-Sleep -Milliseconds 900
  # Insert Table dialog: focus lands on "Number of columns" (text selected). Set 3 cols, Tab to rows, 3, then OK (Enter).
  $wsh.SendKeys('3'); Start-Sleep -Milliseconds 150
  $wsh.SendKeys('{TAB}'); Start-Sleep -Milliseconds 150
  $wsh.SendKeys('3'); Start-Sleep -Milliseconds 150
  $wsh.SendKeys('{ENTER}'); Start-Sleep -Milliseconds 700

  $out = "$tmp\rw-uia-table.docx"
  if (Test-Path $out) { Remove-Item $out -Force }
  $doc.SaveAs2($out, 16); $doc.Close($false)
  $body = Read-Part $out 'word/document.xml'
  $log += "tbl_present=$([bool]($body -match '<w:tbl>'))"
  $log += "rows=$(([regex]::Matches($body, '<w:tr\b')).Count)"
  $log += "gridCol_count=$(([regex]::Matches($body, '<w:gridCol\b')).Count)"
  $log += "tcs=$(([regex]::Matches($body, '<w:tc>')).Count)"
  $log += "tblStyle=$(if ($body -match 'w:tblStyle[^>]*w:val=\"([^\"]*)\"') { $Matches[1] } else { 'NONE' })"
  $log += "tblLook=$(if ($body -match '<w:tblLook\b[^>]*/?>') { ($Matches[0] -replace '\s+', ' ') } else { 'NONE' })"
  $log += "tblBorders=$([bool]($body -match '<w:tblBorders>'))"
  $log += "tblW=$(if ($body -match '<w:tblW\b[^>]*/?>') { ($Matches[0] -replace '\s+', ' ') } else { 'NONE' })"
  $log += "tcMar=$([bool]($body -match '<w:tblCellMar>'))"
  $log += "firstGridCol=$(if ($body -match '<w:gridCol\b[^>]*/?>') { $Matches[0] } else { 'NONE' })"
} catch { $log += "ERR: $($_.Exception.Message)" }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
