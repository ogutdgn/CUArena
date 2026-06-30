param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Add()
    $rng = $doc.Range()
    $null = $doc.Tables.Add($rng, 3, 3)   # 3 rows x 3 cols
    if (Test-Path $Out) { Remove-Item $Out -Force }
    $doc.SaveAs2($Out, 16)
    $doc.Close($false)
    Write-Output "saved: $Out"
} finally {
    $w.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
