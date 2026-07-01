# Table Styles (Table Design tab) measurement: what OOXML real Word writes when a built-in table
# style is applied via the gallery (COM $tbl.Style = ...), and when it is CLEARED back to Table Normal.
# Captures tblStyle ref, tblLook, and every cnfStyle (row + cell) shape. Invisible, pure COM. PID-safe.
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
function Has-StyleDef($docx, $styleId) {
  $zip = [System.IO.Compression.ZipFile]::OpenRead($docx)
  try { $e = $zip.Entries | Where-Object { $_.FullName -eq 'word/styles.xml' } | Select-Object -First 1
    if (-not $e) { return $false }
    $sr = New-Object System.IO.StreamReader($e.Open()); try { $x = $sr.ReadToEnd() } finally { $sr.Dispose() }
    return [bool]($x -match ('w:styleId="' + [regex]::Escape($styleId) + '"')) }
  finally { $zip.Dispose() }
}
$tmp = "C:\tmp\wc-oracle-tblstyles"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
$spawned = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id | Where-Object { $pre -notcontains $_ })
$log = @()
function Summarize($tag, $b) {
  $ts  = if ($b -match '<w:tblStyle\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $tl  = if ($b -match '<w:tblLook\b[^>]*/?>') { ($Matches[0] -replace '\s+',' ') } else { 'none' }
  $cnf = [regex]::Matches($b, '<w:cnfStyle\b[^>]*/?>') | ForEach-Object { ($_.Value -replace '\s+',' ') }
  $shd = ([regex]::Matches($b, '<w:shd\b')).Count
  $script:log += "  [$tag] tblStyle=$ts"
  $script:log += "         tblLook=$tl"
  $script:log += "         cnfStyle count=$($cnf.Count) | direct <w:shd> count=$shd"
  ($cnf | Select-Object -First 4) | ForEach-Object { $script:log += "           $_" }
}
try {
  # Enumerate a few candidate built-in style display names to find one that applies in this build.
  $candidates = 'Grid Table 4 Accent 1','Grid Table 4 - Accent 1','List Table 3 Accent 1','Grid Table 5 Dark Accent 1','Table Grid Light'
  $applyName = $null
  $doc0 = $w.Documents.Add()
  $t0 = $doc0.Tables.Add($doc0.Range(0,0), 3, 3, 1, 0); $t0.Style = 'Table Grid'
  foreach ($nm in $candidates) {
    try { $t0.Style = $nm; $applyName = $nm; break } catch {}
  }
  $doc0.Close($false)
  $log += "== applied built-in style name: '$applyName' =="
  if (-not $applyName) { throw "no candidate built-in table style name applied in this build" }

  # (A) apply the built-in style
  $out = "$tmp\applied.docx"
  $docA = $w.Documents.Add()
  $tA = $docA.Tables.Add($docA.Range(0,0), 3, 3, 1, 0); $tA.Style = 'Table Grid'
  # put some text so header/first-column banding has cells to key on
  $tA.Cell(1,1).Range.Text = 'H1'; $tA.Cell(1,2).Range.Text = 'H2'; $tA.Cell(2,1).Range.Text = 'a'
  $tA.Style = $applyName
  $sid = $tA.Style.NameLocal
  $docA.SaveAs2($out, 16); $docA.Close($false)
  $bA = Read-Body $out
  $log += "== (A) applied '$applyName' (NameLocal=$sid) =="
  Summarize 'applied' $bA
  $refId = if ($bA -match '<w:tblStyle w:val="([^"]+)"') { $Matches[1] } else { $null }
  if ($refId) { $log += "         tblStyle val='$refId' defined in styles.xml? " + (Has-StyleDef $out $refId) }

  # (B) apply, then toggle Header Row + Banded Rows Table Style Options, capture cnfStyle
  $out2 = "$tmp\applied-opts.docx"
  $docB = $w.Documents.Add()
  $tB = $docB.Tables.Add($docB.Range(0,0), 3, 3, 1, 0); $tB.Style = 'Table Grid'
  $tB.Style = $applyName
  $tB.Select()
  foreach ($m in 'TableStyleHeaderRowWord','TableStyleBandedRowsWord') { try { $w.CommandBars.ExecuteMso($m) } catch {} }
  $docB.SaveAs2($out2, 16); $docB.Close($false)
  $bB = Read-Body $out2
  $log += "== (B) applied '$applyName' + Header Row + Banded Rows =="
  Summarize 'applied+opts' $bB

  # (C) CLEAR: apply a style, then reset to Table Normal (Word's 'Clear' in the gallery)
  $out3 = "$tmp\cleared.docx"
  $docC = $w.Documents.Add()
  $tC = $docC.Tables.Add($docC.Range(0,0), 3, 3, 1, 0); $tC.Style = 'Table Grid'
  $tC.Style = $applyName
  # Clear -> Table Normal (built-in 'Normal Table' / 'Table Normal')
  $cleared = $false
  foreach ($nm in 'Table Normal','Normal Table') { try { $tC.Style = $nm; $cleared = $true; break } catch {} }
  $docC.SaveAs2($out3, 16); $docC.Close($false)
  $bC = Read-Body $out3
  $log += "== (C) cleared to Table Normal (ok=$cleared) =="
  Summarize 'cleared' $bC
} catch { $log += "ERR: $($_.Exception.Message)" }
finally {
  try { $w.Quit() } catch {}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  foreach ($id in $spawned) { try { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } catch {} }
}
$log | ForEach-Object { Write-Output $_ }
