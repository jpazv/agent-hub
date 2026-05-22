# hub-down.ps1
# Consome o estado mais recente do hub a partir do GitHub.
# Execute ao comecar o dia ou antes de iniciar uma sessao.

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

Write-Host "hub-down: sincronizando $HubPath ..."
Push-Location $HubPath
git pull
Pop-Location
Write-Host "hub-down: concluido."
