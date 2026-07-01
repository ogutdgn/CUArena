# Extract a BATCH of Word table style definitions (reliable chunks under the timeout).
# Reads style names from -NamesFile, applies names[Start..Start+Count-1] each to a 2x2 table,
# saves, and writes word/styles.xml to -Out. Visible Word. PID-safe.
param(
  [string]$NamesFile = 'C:\tmp\modern-tablestyles.txt',
  [int]$Start = 0,
  [int]$Count = 30,
  [string]$Out = 'C:\tmp\word-tblstyles-batch.xml'
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$all = @(Get-Content -LiteralPath $NamesFile | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
$end = [Math]::Min($Start + $Count - 1, $all.Count - 1)
$batch = @($all[$Start..$end])
$tmp = 'C:\tmp\wc-oracle-tblcat'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $true; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
try {
  $doc = $w.Documents.Add()
  $applied = 0
  foreach ($nm in $batch) {
    try {
      $rng = $doc.Range($doc.Content.End - 1, $doc.Content.End - 1)
      $t = $doc.Tables.Add($rng, 2, 2, 1, 0)
      $t.Style = $nm
      $doc.Range($doc.Content.End - 1, $doc.Content.End - 1).InsertParagraphAfter()
      $applied++
    } catch { $log += ("apply FAIL " + $nm) }
  }
  $f = Join-Path $tmp ('batch-' + $Start + '.docx')
  if (Test-Path $f) { Remove-Item -LiteralPath $f -Force }
  $doc.SaveAs2($f, 16); $doc.Close($false)
  $zip = [System.IO.Compression.ZipFile]::OpenRead($f)
  try {
    $e = $zip.Entries | Where-Object { $_.FullName -eq 'word/styles.xml' } | Select-Object -First 1
    $sr = New-Object System.IO.StreamReader($e.Open()); try { $xml = $sr.ReadToEnd() } finally { $sr.Dispose() }
    Set-Content -LiteralPath $Out -Value $xml -Encoding UTF8
    $cnt = ([regex]::Matches($xml, '<w:style [^>]*w:type="table"')).Count
    $log += ("batch " + $Start + ".." + $end + " applied=" + $applied + " -> " + $Out + " tableStyles=" + $cnt)
  } finally { $zip.Dispose() }
} catch { $log += ("ERR: " + $_.Exception.Message) }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
