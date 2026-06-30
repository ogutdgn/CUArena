param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Add()
    $doc.Content.Text = 'Hello world'
    $footer = $doc.Sections.Item(1).Footers.Item(1).Range   # wdHeaderFooterPrimary
    $null = $doc.Fields.Add($footer, 33)                     # wdFieldPage = 33
    if (Test-Path $Out) { Remove-Item $Out -Force }
    $doc.SaveAs2($Out, 16)
    $doc.Close($false)
    Write-Output "saved: $Out"
} finally {
    $w.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
