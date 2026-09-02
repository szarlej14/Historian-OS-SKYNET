param([string]$VaultRoot = ".")

Set-Location $VaultRoot

$dirs = @(
  "00 Relacje","10 Miejsca","20 Wydarzenia","30 Zrodla",
  "40 Fakty","50 Serie","60 Command Center","Templates",
  ".obsidian/snippets"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

function Copy-IfExists($Source, $Destination) {
  if (Test-Path $Source) {
    Copy-Item $Source $Destination -Force
    Write-Host "OK  $Destination"
  } else {
    Write-Host "WARN brak: $Source"
  }
}

Copy-IfExists "Templates/Relacja.md" "00 Relacje/_README.md"
Copy-IfExists "Templates/Wydarzenie.md" "20 Wydarzenia/_README.md"
Copy-IfExists "Templates/Seria.md" "50 Serie/_README.md"
Copy-IfExists "Dashboard.md" "60 Command Center/Dashboard.md"

Write-Host ""
Write-Host "Historian OS SKYNET vault structure ready."
Write-Host "Enable SKYNET CSS: Settings > Appearance > CSS snippets."
