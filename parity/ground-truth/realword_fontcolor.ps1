# Real-Word font-color ground truth via COM (Font.Color == ribbon Font Color).
# SAFE ONLY WHEN NO OTHER WORD IS OPEN (Quit would close it).
param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
$pre = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -Expand Id)
if ($pre.Count -gt 0) { Write-Error "WINWORD already running (PIDs: $($pre -join ',')). Close Word first."; exit 2 }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Add()
    $doc.Content.Text = 'Revenue'
    $r = $doc.Range(0, 7)            # "Revenue"
    $r.Font.Color = 255             # RGB(255,0,0) = FF0000 (red) -> <w:color w:val="FF0000">
    if (Test-Path $Out) { Remove-Item $Out -Force }
    $doc.SaveAs2($Out, 16)          # wdFormatDocumentDefault = .docx
    $doc.Close($false)
    Write-Output "saved: $Out"
} finally {
    $w.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
