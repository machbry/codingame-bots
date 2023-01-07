$botsDir = "bots"
$challengePackageName = "challengelibs"
$challengeName = Read-Host "Enter challenge name"

$challengeName = ($challengeName -replace ' ', '_').ToLower()
$challengeDir = "$botsDir\$challengeName"
if (Test-Path $challengeDir) {
    Write-Host "A challenge with the same name already exists. Init not done."
} else
{
    $challengePackageDir = "$challengeDir\$challengePackageName"
    New-Item -ItemType Directory -Path $challengeDir
    New-Item -ItemType File -Path "$challengeDir\bot.py"
    New-Item -ItemType Directory -Path "$challengePackageDir"
    New-Item -ItemType File -Path "$challengePackageDir\__init__.py"
    git add "$challengeDir\bot.py"
    git add "$challengePackageDir\__init__.py"
}
