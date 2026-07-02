# Extract Word's built-in table style DEFINITIONS. Iterates the document's Styles collection for
# table styles (Type=wdStyleTypeTable=3), applies each to a small table so Word writes its full
# <w:style w:type="table"> def to word/styles.xml, saves, and copies styles.xml out for parsing.
# Uses a VISIBLE Word instance (more reliable than invisible here). PID-safe.
param([int]$Max = 200, [string]$Out = 'C:\tmp\word-tablestyles.xml', [string]$Names = 'C:\tmp\word-tablestyle-names.txt',
  [string]$Filter = '', [string]$Progress = 'C:\tmp\word-tablestyles-progress.txt')
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$tmp = 'C:\tmp\wc-oracle-tblcat'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $true; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
try {
  $doc = $w.Documents.Add()
  # 1) collect table style names (Type 3 = wdStyleTypeTable)
  $tblNames = New-Object System.Collections.ArrayList
  foreach ($st in $doc.Styles) {
    try { if ($st.Type -eq 3) { [void]$tblNames.Add($st.NameLocal) } } catch {}
  }
  $log += ("table styles available: " + $tblNames.Count)
  Set-Content -LiteralPath $Names -Value ($tblNames -join "`n") -Encoding UTF8
  # optional name filter (regex on NameLocal) — e.g. the ~113 modern gallery styles
  $target = if ($Filter) { @($tblNames | Where-Object { $_ -match $Filter }) } else { $tblNames }
  $log += ("target after filter: " + $target.Count)
  # 2) apply each to a fresh 2x2 table so Word persists its definition
  $applied = 0
  foreach ($nm in $target) {
    if ($applied -ge $Max) { break }
    try {
      $rng = $doc.Range($doc.Content.End - 1, $doc.Content.End - 1)
      $t = $doc.Tables.Add($rng, 2, 2, 1, 0)
      $t.Style = $nm
      $doc.Range($doc.Content.End - 1, $doc.Content.End - 1).InsertParagraphAfter()
      $applied++
      if ($applied % 10 -eq 0) { Set-Content -LiteralPath $Progress -Value ("applied $applied / $($target.Count)") -Encoding UTF8 }
    } catch { $log += ("apply FAIL " + $nm + ": " + $_.Exception.Message) }
  }
  $log += ("applied: " + $applied)
  Set-Content -LiteralPath $Progress -Value ("apply-done $applied; saving...") -Encoding UTF8
  $f = Join-Path $tmp 'catalog.docx'
  if (Test-Path $f) { Remove-Item -LiteralPath $f -Force }
  $doc.SaveAs2($f, 16); $doc.Close($false)
  # 3) copy word/styles.xml out
  $zip = [System.IO.Compression.ZipFile]::OpenRead($f)
  try {
    $e = $zip.Entries | Where-Object { $_.FullName -eq 'word/styles.xml' } | Select-Object -First 1
    $sr = New-Object System.IO.StreamReader($e.Open()); try { $xml = $sr.ReadToEnd() } finally { $sr.Dispose() }
    Set-Content -LiteralPath $Out -Value $xml -Encoding UTF8
    $tblStyleCount = ([regex]::Matches($xml, '<w:style [^>]*w:type="table"')).Count
    $log += ("styles.xml written: " + $Out + " | <w:style type=table> count=" + $tblStyleCount)
  } finally { $zip.Dispose() }
} catch { $log += ("ERR: " + $_.Exception.Message) }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
