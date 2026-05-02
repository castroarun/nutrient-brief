# _ship_edition_001.ps1
# One-shot: copy Edition 001 binaries from Cowork staging → git commit → push.
# Safe to re-run: if files already exist, overwrites; git commit skipped on no-op.

$ErrorActionPreference = "Stop"
$RepoRoot   = "C:\Users\Castro\nutrient-brief"
$EditionDir = Join-Path $RepoRoot "content\editions\001_magnesium-glycinate"

Write-Host "== Edition 001 Ship Script ==" -ForegroundColor Cyan

# ---------- 1. Locate the Cowork staging folder ----------
$StageName    = "_edition_001_staging"
$CoworkFolder = "Comprehensive Research for new workflows"

$SearchRoots = @(
  "$env:USERPROFILE\Documents",
  "$env:USERPROFILE\Desktop",
  "$env:USERPROFILE\Downloads",
  "$env:USERPROFILE\OneDrive\Documents",
  "$env:USERPROFILE\OneDrive - Personal\Documents",
  "$env:USERPROFILE"
)

$Staging = $null
foreach ($root in $SearchRoots) {
  if (-not (Test-Path $root)) { continue }
  $hits = Get-ChildItem -Path $root -Filter $CoworkFolder -Directory -Recurse -ErrorAction SilentlyContinue -Depth 4 |
          Select-Object -First 1
  if ($hits) {
    $candidate = Join-Path $hits.FullName $StageName
    if (Test-Path $candidate) { $Staging = $candidate; break }
  }
}

if (-not $Staging) {
  Write-Host "Staging folder not found in standard locations." -ForegroundColor Red
  Write-Host "Please run this script with -StagingPath '<full path>' or drop the folder at:"
  Write-Host "  $env:USERPROFILE\Documents\$CoworkFolder\$StageName"
  exit 1
}
Write-Host "Found staging: $Staging" -ForegroundColor Green

# ---------- 2. Copy the 10 files ----------
if (-not (Test-Path "$EditionDir\carousel")) { New-Item -ItemType Directory -Path "$EditionDir\carousel" -Force | Out-Null }
if (-not (Test-Path "$EditionDir\assets"))   { New-Item -ItemType Directory -Path "$EditionDir\assets"   -Force | Out-Null }

Copy-Item -Path (Join-Path $Staging "share-card.html")      -Destination $EditionDir -Force
Copy-Item -Path (Join-Path $Staging "share-card.pdf")       -Destination $EditionDir -Force
Copy-Item -Path (Join-Path $Staging "carousel\*.html")      -Destination (Join-Path $EditionDir "carousel") -Force
Copy-Item -Path (Join-Path $Staging "assets\*.png")         -Destination (Join-Path $EditionDir "assets")   -Force

Write-Host "Files copied." -ForegroundColor Green
Get-ChildItem $EditionDir -Recurse -File | Select-Object FullName, Length | Format-Table -AutoSize

# ---------- 3. Git commit + push ----------
Set-Location $RepoRoot
git add -A
$pending = git status --porcelain
if ([string]::IsNullOrWhiteSpace($pending)) {
  Write-Host "Nothing to commit." -ForegroundColor Yellow
} else {
  git commit -m "Edition 001: Magnesium Glycinate — repo scaffold + first edition + GitHub Pages + cron"
  Write-Host "Commit created. Pushing to origin/main..." -ForegroundColor Cyan
  git push origin main
}

Write-Host ""
Write-Host "== Done. Next steps (browser, one-time) ==" -ForegroundColor Cyan
Write-Host "1. https://github.com/castroarun/nutrient-brief/settings/pages"
Write-Host "   -> Source: Deploy from a branch | Branch: main / (root) | Save"
Write-Host "2. https://github.com/castroarun/nutrient-brief/settings/secrets/actions"
Write-Host "   -> Add:  ANTHROPIC_API_KEY  WHATSAPP_TOKEN  WHATSAPP_PHONE_NUMBER_ID  WHATSAPP_TO"
Write-Host "3. After ~60s, test: https://castroarun.github.io/nutrient-brief/"
