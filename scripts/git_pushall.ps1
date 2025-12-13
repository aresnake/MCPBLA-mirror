Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Toujours exécuter depuis la racine du repo
$repoRoot = (git rev-parse --show-toplevel).Trim()
cd $repoRoot

git add .
# commit seulement si nécessaire
$st = (git status --porcelain)
if ($st) {
  git commit -m "wip"
} else {
  Write-Host "Nothing to commit (working tree clean)"
}

git push origin main
git push mirror main

$sha = (git rev-parse HEAD).Trim()
Write-Host "==============================="
Write-Host "LAST COMMIT SHA: $sha"
Write-Host "==============================="
