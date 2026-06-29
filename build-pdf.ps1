# PowerShell script to build Persian PDF with xepersian
# Usage: .\build-pdf.ps1

$ErrorActionPreference = "Stop"

Write-Host "Step 1: Generating tex file with Quarto..." -ForegroundColor Cyan
quarto render --to pdf --no-execute

Write-Host "Step 2: Finding generated tex file..." -ForegroundColor Cyan
$texFile = Get-ChildItem *.tex | Where-Object { $_.Name -notmatch "^(test|check)\.tex$" } | Select-Object -First 1

if (-not $texFile) {
    Write-Error "No tex file found!"
    exit 1
}

Write-Host "  Found: $($texFile.Name)" -ForegroundColor Green

Write-Host "Step 3: Patching tex file with xepersian..." -ForegroundColor Cyan
$lines = [System.IO.File]::ReadAllLines($texFile.FullName)

# Insert xepersian after the last \usepackage{etoolbox} line
$xepersianBlock = @(
    "",
    "\usepackage{xepersian}",
    "\settextfont{Gandom}",
    "\setlatintextfont{Times New Roman}",
    ""
)

$lastEtoolboxIdx = -1
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match '\\usepackage\{etoolbox\}') {
        $lastEtoolboxIdx = $i
        break
    }
}

Write-Host "  Found last etoolbox at line $($lastEtoolboxIdx + 1)" -ForegroundColor Yellow

if ($lastEtoolboxIdx -ge 0) {
    $newLines = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $newLines.Add($lines[$i])
        if ($i -eq $lastEtoolboxIdx) {
            foreach ($line in $xepersianBlock) {
                $newLines.Add($line)
            }
        }
    }
    [System.IO.File]::WriteAllLines($texFile.FullName, $newLines)
}

Write-Host "  Patched successfully" -ForegroundColor Green

Write-Host "Step 4: Running xelatex (first pass)..." -ForegroundColor Cyan
& xelatex -interaction=nonstopmode $texFile.Name

Write-Host "Step 5: Running xelatex (second pass)..." -ForegroundColor Cyan
& xelatex -interaction=nonstopmode $texFile.Name

Write-Host "Step 6: Copying PDF to _book/..." -ForegroundColor Cyan
$pdfName = $texFile.Name -replace '\.tex$', '.pdf'
if (Test-Path $pdfName) {
    Copy-Item $pdfName "_book/Faculty-Math-Sciences.pdf" -Force
    Write-Host "  Copied to _book/Faculty-Math-Sciences.pdf" -ForegroundColor Green
}

Write-Host "Done! Check _book/ for outputs." -ForegroundColor Green
