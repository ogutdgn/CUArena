# Extract REAL Word table-style DEFINITIONS, one docx per style (FIX 1 ground truth).
# LESSON (2026-07-02, re-confirming the archive): ONE Word instance reused across docs HANGS
# (0 files after 8 min even for 3 styles). The pattern proven 48x in the pilot is a FRESH
# instance per capture - so this runner spawns ONE WORD PER STYLE (~6s each). PID-safe.
# Resumable: existing outputs are skipped, so re-running continues where it stopped.
# Usage: powershell -File _extract_style_defs.ps1 -NamesFile C:\tmp\names.txt -OutDir C:\tmp\wc-styledefs [-Limit 3]
param(
  [Parameter(Mandatory = $true)][string]$NamesFile,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [int]$Limit = 0
)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$names = Get-Content $NamesFile | Where-Object { $_.Trim() -ne '' }
if ($Limit -gt 0) { $names = $names | Select-Object -First $Limit }
$ok = 0; $fail = 0
foreach ($name in $names) {
    $safe = ($name -replace '[^A-Za-z0-9]', '')
    $out = Join-Path $OutDir ("def-" + $safe + ".docx")
    if (Test-Path $out) { $ok++; Write-Output ("SKIP (exists): " + $name); continue }
    $w = $null
    try {
        $w = New-Object -ComObject Word.Application
        $w.Visible = $false
        $w.DisplayAlerts = 0
        $doc = $w.Documents.Add()
        $tbl = $doc.Tables.Add($doc.Range(0, 0), 2, 2, 1, 0)
        $tbl.Style = $name
        $doc.SaveAs2($out, 16)
        $doc.Close($false)
        $ok++
        Write-Output ("OK: " + $name)
    } catch {
        $fail++
        Write-Output ("FAIL: " + $name + " -> " + $_.Exception.Message)
    } finally {
        if ($w) {
            try { $w.Quit() } catch {}
            [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
        }
        [GC]::Collect(); [GC]::WaitForPendingFinalizers()
        # kill any WINWORD this iteration left behind (never the user's - $pre was empty)
        Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object { $pre -notcontains $_.Id } |
            ForEach-Object { try { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue } catch {} }
    }
}
Write-Output ("DONE ok=" + $ok + " fail=" + $fail + " -> " + $OutDir)
