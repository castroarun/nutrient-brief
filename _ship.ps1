# _ship.ps1 -- minimal Edition 001 ship script
# Usage:
#   .\_ship.ps1                                    # auto-search common locations
#   .\_ship.ps1 -StagingPath 'C:\full\path'        # explicit path

param(
    [string]$StagingPath = ''
)

$ErrorActionPreference = 'Stop'
$RepoRoot   = 'C:\Users\Castro\nutrient-brief'
$EditionDir = 'C:\Users\Castro\nutrient-brief\content\editions\001_magnesium-glycinate'
$CoworkName = 'Comprehensive Research for new workflows'
$StageName  = '_edition_001_staging'

Write-Host '== Edition 001 Ship ==' -ForegroundColor Cyan

# Step 1: locate staging folder
if ($StagingPath -ne '' -and (Test-Path $StagingPath)) {
    $Staging = $StagingPath
}
else {
    $candidates = @(
        (Join-Path $env:USERPROFILE "PycharmProjects\$CoworkName\$StageName"),
        (Join-Path $env:USERPROFILE "Documents\$CoworkName\$StageName"),
        (Join-Path $env:USERPROFILE "OneDrive\Documents\$CoworkName\$StageName"),
        (Join-Path $env:USERPROFILE "Desktop\$CoworkName\$StageName"),
        (Join-Path $env:USERPROFILE "Downloads\$CoworkName\$StageName")
    )
    $Staging = $null
    foreach ($c in $candidates) {
        if (Test-Path $c) { $Staging = $c; break }
    }
}

if (-not $Staging) {
    Write-Host 'Staging folder not found.' -ForegroundColor Red
    Write-Host 'Re-run with explicit path:'
    Write-Host "  .\_ship.ps1 -StagingPath 'C:\full\path\to\_edition_001_staging'"
    exit 1
}

Write-Host "Staging: $Staging" -ForegroundColor Green

# Step 2: ensure target subfolders exist
New-Item -ItemType Directory -Path "$EditionDir\carousel" -Force | Out-Null
New-Item -ItemType Directory -Path "$EditionDir\assets" -Force | Out-Null

# Step 3: copy 10 files
Copy-Item "$Staging\share-card.html" $EditionDir -Force
Copy-Item "$Staging\share-card.pdf"  $EditionDir -Force
Copy-Item "$Staging\carousel\*.html" "$EditionDir\carousel" -Force
Copy-Item "$Staging\assets\*.png"    "$EditionDir\assets" -Force
Write-Host 'Files copied.' -ForegroundColor Green

# Step 4: git add/commit/push
Set-Location $RepoRoot
git add -A
$pending = git status --porcelain
if ([string]::IsNullOrWhiteSpace($pending)) {
    Write-Host 'Nothing to commit.' -ForegroundColor Yellow
}
else {
    git commit -m 'Edition 001 + cloud pipeline + email/whatsapp delivery'
    git push origin main
    Write-Host 'Pushed.' -ForegroundColor Green
}

Write-Host ''
Write-Host '== Next steps (browser, one-time) ==' -ForegroundColor Cyan
Write-Host '1. Pages config:    https://github.com/castroarun/nutrient-brief/settings/pages'
Write-Host '   Source: Deploy from a branch  |  Branch: main /(root)  |  Save'
Write-Host '2. Secrets config:  https://github.com/castroarun/nutrient-brief/settings/secrets/actions'
Write-Host '   Add: EMAIL_FROM, EMAIL_APP_PASSWORD, EMAIL_TO_SELF (see DELIVERY_SETUP.md)'
Write-Host '3. After 60s test:  https://castroarun.github.io/nutrient-brief/'
