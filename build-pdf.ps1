$ErrorActionPreference = "Stop"
Write-Host "Generating PDF..." -ForegroundColor Cyan

quarto render --to pdf --no-execute

$texFile = Get-ChildItem *.tex | Where-Object { $_.Name -notmatch "^(test|check)" } | Select-Object -First 1
if (-not $texFile) { Write-Error "No tex!"; exit 1 }

$lines = [System.IO.File]::ReadAllLines($texFile.FullName)
$xep = @("", "\usepackage{xepersian}", "\settextfont{Gandom}", "\setlatintextfont{Times New Roman}", "")
$lastIdx = -1
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match '\\usepackage\{etoolbox\}') { $lastIdx = $i; break }
}
if ($lastIdx -ge 0) {
    $new = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $new.Add($lines[$i])
        if ($i -eq $lastIdx) { foreach ($l in $xep) { $new.Add($l) } }
    }
    [System.IO.File]::WriteAllLines($texFile.FullName, $new)
    Write-Host "Patched xepersian at line $($lastIdx+1)" -ForegroundColor Green
}

xelatex -interaction=nonstopmode $texFile.Name
xelatex -interaction=nonstopmode $texFile.Name

$pdf = $texFile.Name -replace '\.tex$','.pdf'
if (Test-Path $pdf) {
    Copy-Item $pdf "_book/Faculty-Math-Sciences.pdf" -Force
    Write-Host "Done!" -ForegroundColor Green
}
