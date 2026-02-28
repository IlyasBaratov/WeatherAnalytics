<#
Deploy (build + push) a single combined image (UI + API) to ACR using Azure CLI only,
then update the Azure App Service to run that image.

- Combined image repo: weather-portal:<tag> (root Dockerfile)

Requires:
- Azure CLI (`az`) installed
- `az login` already completed

Usage (PowerShell):
  .\deploy.ps1

Optional overrides:
  .\deploy.ps1 -SubscriptionId "..." -ResourceGroup "..." -AcrName "..." -Tag "latest"
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $false)]
  [string]$SubscriptionId = "6767198a-fc97-4598-b7f4-17496c2cc64e",

  [Parameter(Mandatory = $false)]
  [string]$ResourceGroup = "rg-app-weather-analytics",

  [Parameter(Mandatory = $false)]
  [string]$AcrName = "acrweatheranalyticswus2",

  [Parameter(Mandatory = $false)]
  [ValidateNotNullOrEmpty()]
  [string]$Tag = "latest"

  ,
  [Parameter(Mandatory = $false)]
  [ValidateNotNullOrEmpty()]
  [string]$WebAppName = "app-weather-analytics"

  ,
  [Parameter(Mandatory = $false)]
  [ValidateNotNullOrEmpty()]
  [string]$ImageRepository = "weather-portal"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Az {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Args
  )

  & az @Args
  if ($LASTEXITCODE -ne 0) {
    $argText = ($Args -join ' ')
    throw "Azure CLI command failed (exit $LASTEXITCODE): az $argText"
  }
}

function Assert-CommandExists {
  param([Parameter(Mandatory=$true)][string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Required command not found: '$Name'. Install it and retry."
  }
}

# Winget installs Azure CLI to a standard location, but the current terminal session
# might not see the updated PATH yet. Fall back to calling az via full path.
$azCommand = (Get-Command "az" -ErrorAction SilentlyContinue)
if (-not $azCommand) {
  $azCandidates = @(
    "$env:ProgramFiles\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd",
    "$env:ProgramFiles(x86)\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd",
    "$env:LocalAppData\\Microsoft\\WindowsApps\\az.cmd"
  )
  $azPath = $azCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($azPath) {
    function az {
      param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
      & $azPath @Args
    }
  }
}

Assert-CommandExists -Name "az"

# Ensure we run from repo root (where Dockerfile lives)
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path -Path (Join-Path $repoRoot "Dockerfile"))) {
  throw "Dockerfile not found in repo root. Run this script from the repository root."
}

Write-Host "Using subscription: $SubscriptionId"
Write-Host "Using resource group: $ResourceGroup"
Write-Host "Using ACR: $AcrName"
Write-Host "Using tag: $Tag" 
Write-Host "Using web app: $WebAppName"
Write-Host "Using image repo: $ImageRepository"

Write-Host "Setting active subscription..."
Invoke-Az -Args @('account','set','-s',$SubscriptionId) | Out-Null

Write-Host "Verifying ACR exists..."
Invoke-Az -Args @('acr','show','-g',$ResourceGroup,'-n',$AcrName) 1>$null

$acrLoginServer = (& az acr show -g $ResourceGroup -n $AcrName --query loginServer -o tsv)
if ($LASTEXITCODE -ne 0 -or -not $acrLoginServer) {
  throw "Failed to resolve ACR loginServer for '$AcrName'."
}

$fullImageName = "$acrLoginServer/$ImageRepository`:$Tag"

# Helpful diagnostics for common ACR policy combos that can break/deny ACR Tasks pushes.
$acrInfoJson = & az acr show -g $ResourceGroup -n $AcrName --query "{roleAssignmentMode:roleAssignmentMode, authAsArm:policies.azureAdAuthenticationAsArmPolicy.status}" -o json
if ($LASTEXITCODE -eq 0 -and $acrInfoJson) {
  try {
    $acrInfo = $acrInfoJson | ConvertFrom-Json
    if ($acrInfo.roleAssignmentMode -and $acrInfo.roleAssignmentMode -ne 'LegacyRegistryPermissions') {
      Write-Host "WARNING: ACR roleAssignmentMode is '$($acrInfo.roleAssignmentMode)'. If pushes are denied, consider: az acr update -g $ResourceGroup -n $AcrName --set roleAssignmentMode=LegacyRegistryPermissions" -ForegroundColor Yellow
    }
    if ($acrInfo.authAsArm -and $acrInfo.authAsArm -ne 'disabled') {
      Write-Host "WARNING: ACR authentication-as-ARM policy is '$($acrInfo.authAsArm)'. If you see 'push credential required' in builds, consider: az acr config authentication-as-arm update -r $AcrName --status disabled" -ForegroundColor Yellow
    }
  } catch {
    # Non-fatal; continue.
  }
}

Write-Host "Building + pushing combined image to ACR: $($ImageRepository):$Tag"
try {
  Invoke-Az -Args @('acr','build','-g',$ResourceGroup,'-r',$AcrName,'-t',"$($ImageRepository):$Tag",'-f','Dockerfile','.')
} catch {
  if ($_.Exception.Message -match 'TasksOperationsNotAllowed') {
    throw "ACR Tasks are not permitted for '$AcrName' in subscription '$SubscriptionId'. This blocks 'az acr build'. You will need to (1) request enabling ACR Tasks / remove policy restriction, or (2) build images elsewhere (e.g., GitHub Actions) and push to ACR. Original error: $($_.Exception.Message)"
  }
  throw
}

Write-Host "Updating App Service container to: $fullImageName"
Invoke-Az -Args @(
  'webapp','config','container','set',
  '-g',$ResourceGroup,
  '-n',$WebAppName,
  '--docker-custom-image-name',$fullImageName,
  '--docker-registry-server-url',("https://{0}" -f $acrLoginServer)
) | Out-Null

# App Service for Containers needs to know what port the container listens on.
Invoke-Az -Args @(
  'webapp','config','appsettings','set',
  '-g',$ResourceGroup,
  '-n',$WebAppName,
  '--settings',
  'WEBSITES_PORT=8000'
) | Out-Null

Write-Host "Restarting web app..."
Invoke-Az -Args @('webapp','restart','-g',$ResourceGroup,'-n',$WebAppName,'-o','none') | Out-Null

$hostName = (& az webapp show -g $ResourceGroup -n $WebAppName --query defaultHostName -o tsv)
if ($LASTEXITCODE -eq 0 -and $hostName) {
  Write-Host "Deployed. URLs:"
  Write-Host ("  UI:   https://{0}/html/index.html" -f $hostName)
  Write-Host ("  API:  https://{0}/api/health" -f $hostName)
  Write-Host ("  Docs: https://{0}/api/docs" -f $hostName)
}
