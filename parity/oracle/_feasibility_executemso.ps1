# Feasibility probe: can we drive the REAL ribbon command via CommandBars.ExecuteMso and capture the output?
# This is the ground-truth mechanism the parity oracle needs — ExecuteMso runs the ribbon button's actual code
# path (e.g. the multilevel Bullets gallery), unlike COM scripting (ListFormat.ApplyBulletDefault = single-level).
# PID-safe: aborts if any WINWORD is already open; kills only the spawned instance.
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }

Add-Type -AssemblyName System.IO.Compression.FileSystem
function Read-Part($docx, $part) {
  $zip = [System.IO.Compression.ZipFile]::OpenRead($docx)
  try {
    $e = $zip.Entries | Where-Object { $_.FullName -eq $part } | Select-Object -First 1
    if (-not $e) { return $null }
    $sr = New-Object System.IO.StreamReader($e.Open())
    try { return $sr.ReadToEnd() } finally { $sr.Dispose() }
  } finally { $zip.Dispose() }
}

$tmp = "C:\tmp\wc-oracle-feas"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$results = @{}
try {
  # --- Test 1: a simple button — ExecuteMso("Bold") on a selection ---
  $doc = $w.Documents.Add()
  $doc.Content.Text = 'Revenue'
  $doc.Range(0, 7).Select()
  $w.CommandBars.ExecuteMso('Bold')
  $out1 = "$tmp\rw-mso-bold.docx"
  if (Test-Path $out1) { Remove-Item $out1 -Force }
  $doc.SaveAs2($out1, 16); $doc.Close($false)
  $body1 = Read-Part $out1 'word/document.xml'
  $results['bold_wb'] = if ($body1 -match '<w:b\b') { 'YES' } else { 'NO' }

  # --- Test 2: a GALLERY — ExecuteMso for the Bullets gallery on a selection ---
  $doc2 = $w.Documents.Add()
  $doc2.Content.Text = 'item'
  $doc2.Range(0, 4).Select()
  $bulletMso = 'BulletsGalleryWord'
  try { $w.CommandBars.ExecuteMso($bulletMso); $results['bullets_exec'] = 'OK' }
  catch { $results['bullets_exec'] = "ERR: $($_.Exception.Message)" }
  $out2 = "$tmp\rw-mso-bullets.docx"
  if (Test-Path $out2) { Remove-Item $out2 -Force }
  $doc2.SaveAs2($out2, 16); $doc2.Close($false)
  $body2 = Read-Part $out2 'word/document.xml'
  $num2 = Read-Part $out2 'word/numbering.xml'
  $results['bullets_numPr'] = if ($body2 -match '<w:numPr\b') { 'YES' } else { 'NO' }
  $results['bullets_multiLevel'] = if ($num2 -match 'multiLevelType[^>]*w:val="(hybridMultilevel|multilevel)"') { 'MULTILEVEL' } elseif ($num2 -match 'multiLevelType[^>]*w:val="singleLevel"') { 'SINGLELEVEL' } else { 'NONE' }
  $results['bullets_numLevels'] = if ($num2) { ([regex]::Matches($num2, '<w:lvl\b')).Count } else { 0 }

  # --- Test 3: can we read the enabled state / a control's presence? (IsEnabledMso) ---
  try { $results['GetEnabledMso_Bold'] = $w.CommandBars.GetEnabledMso('Bold') } catch { $results['GetEnabledMso_Bold'] = "ERR: $($_.Exception.Message)" }
  try { $results['GetLabelMso_Bold'] = $w.CommandBars.GetLabelMso('Bold') } catch { $results['GetLabelMso_Bold'] = "ERR" }
} finally {
  $w.Quit()
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$results.GetEnumerator() | Sort-Object Name | ForEach-Object { Write-Output ("{0} = {1}" -f $_.Name, $_.Value) }
