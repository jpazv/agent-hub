# hub-status.ps1
# Mostra o estado atual do hub: mudancas locais, branch, sync com GitHub.

param(
    [string]$HubPath = ""
)

# Detecta o caminho do hub
if (-not $HubPath) {
    $toml = "$env:USERPROFILE\.config\agents\machine.toml"
    if (Test-Path $toml) {
        $line = Get-Content $toml | Where-Object { $_ -match '^hub_path\s*=' }
        if ($line) {
            $HubPath = ($line -split '=', 2)[1].Trim().Trim('"').Trim("'")
        }
    }
}

if (-not $HubPath -or -not (Test-Path $HubPath)) {
    Write-Error "Hub nao encontrado. Defina hub_path no machine.toml ou passe -HubPath."
    exit 1
}

Push-Location $HubPath

Write-Host ""
Write-Host "=== hub-status ==="
Write-Host "Caminho : $HubPath"
Write-Host "Branch  : $(git branch --show-current)"
Write-Host ""

Write-Host "--- Mudancas locais ---"
$status = git status --porcelain
if ($status) { $status } else { Write-Host "Nenhuma mudanca local." }

Write-Host ""
Write-Host "--- Commits nao enviados ---"
$ahead = git log origin/main..HEAD --oneline 2>/dev/null
if ($ahead) { $ahead } else { Write-Host "Nenhum commit pendente." }

Write-Host ""
Write-Host "--- Ultimo commit ---"
git log -1 --format="%h %ar — %s"

Pop-Location
