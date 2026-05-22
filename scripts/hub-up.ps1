# hub-up.ps1
# Envia o estado atual do hub para o GitHub.
# Execute ao encerrar uma sessao com mudancas relevantes.

param(
    [string]$HubPath = "",
    [string]$Message = ""
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

if (-not $Message) {
    $date = Get-Date -Format "yyyy-MM-dd"
    $machine = $env:COMPUTERNAME
    $Message = "chore: hub-up $date ($machine)"
}

Write-Host "hub-up: verificando mudancas em $HubPath ..."
Push-Location $HubPath

$status = git status --porcelain
if (-not $status) {
    Write-Host "hub-up: nenhuma mudanca para enviar."
    Pop-Location
    exit 0
}

git add .
git commit -m $Message
git push

Pop-Location
Write-Host "hub-up: concluido."
