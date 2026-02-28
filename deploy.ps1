<#
Deploy (build + push) a reusable base image + a small app image to ACR using Azure CLI only.

This script intentionally does NOT update App Service container configuration.
It does restart the specified App Service at the end.

Why two images?
- Base image: OS deps + Python packages (slow to build, changes only when deps change)
- App image: your code + frontend assets (fast to build, changes often)

This script computes a deterministic base tag from Dockerfile.base + backEnd/requirements.txt.
If that base tag already exists in ACR, it skips rebuilding the base and only builds the app delta.

- Combined image repo: weather-portal:<tag> (root Dockerfile)

Requires:
- Azure CLI (`az`) installed
- `az login` already completed

Usage (PowerShell):
  .\deploy.ps1

Optional overrides:
  .\deploy.ps1 -SubscriptionId "..." -ResourceGroup "..." -AcrName "..." -Tag "latest"
  .\deploy.ps1 -ForceRebuildBase
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

  ,
  [Parameter(Mandatory = $false)]
  [switch]$ForceRebuildBase
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

function Get-CombinedSha256 {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Paths
  )

  $sha = [System.Security.Cryptography.SHA256]::Create()
  try {
    foreach ($p in $Paths) {
      $resolved = Join-Path $repoRoot $p
      if (-not (Test-Path -Path $resolved)) {
        throw "Hash input file not found: $p"
      }

      $header = [System.Text.Encoding]::UTF8.GetBytes("PATH:$p`n")
      [void]$sha.TransformBlock($header, 0, $header.Length, $null, 0)

      $bytes = [System.IO.File]::ReadAllBytes($resolved)
      [void]$sha.TransformBlock($bytes, 0, $bytes.Length, $null, 0)

      $footer = [System.Text.Encoding]::UTF8.GetBytes("`nENDPATH`n")
      [void]$sha.TransformBlock($footer, 0, $footer.Length, $null, 0)
    }
    [void]$sha.TransformFinalBlock(@(), 0, 0)
    return ([System.BitConverter]::ToString($sha.Hash)).Replace('-', '').ToLowerInvariant()
  } finally {
    $sha.Dispose()
  }
}

function Test-AcrTagExists {
  param(
    [Parameter(Mandatory = $true)]
    [string]$AcrName,
    [Parameter(Mandatory = $true)]
    [string]$Repository,
    [Parameter(Mandatory = $true)]
    [string]$Tag
  )

  try {
    $count = & az acr repository show-tags -n $AcrName --repository $Repository --query "[?@=='$Tag'] | length(@)" -o tsv 2>$null
    if ($LASTEXITCODE -ne 0) {
      return $false
    }
    return ([int]$count -gt 0)
  } catch {
    return $false
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
Write-Host "Will restart web app: $WebAppName"
Write-Host "Using image repo: $ImageRepository"

Write-Host "Setting active subscription..."
Invoke-Az -Args @('account','set','-s',$SubscriptionId) | Out-Null

# Fast path: ACR login server is typically <registryName>.azurecr.io
$acrLoginServer = ("{0}.azurecr.io" -f $AcrName)

$fullImageName = "$acrLoginServer/$ImageRepository`:$Tag"

$baseRepository = "$ImageRepository-base"
$baseHash = Get-CombinedSha256 -Paths @('Dockerfile.base', 'backEnd/requirements.txt')
$baseTag = ("base-{0}" -f $baseHash.Substring(0, 12))
$fullBaseImageName = "$acrLoginServer/$baseRepository`:$baseTag"

Write-Host "Base image repo: $baseRepository"
Write-Host "Base image tag:  $baseTag"

if ($ForceRebuildBase) {
  Write-Host "ForceRebuildBase set: will rebuild base image." -ForegroundColor Yellow
}

$baseExists = Test-AcrTagExists -AcrName $AcrName -Repository $baseRepository -Tag $baseTag
if ($ForceRebuildBase -or -not $baseExists) {
  Write-Host "Building + pushing BASE image to ACR: $($baseRepository):$baseTag"
  try {
    Invoke-Az -Args @(
      'acr','build',
      '-g',$ResourceGroup,
      '-r',$AcrName,
      '-t',"$($baseRepository):$baseTag",
      '-f','Dockerfile.base','.'
    )
  } catch {
    if ($_.Exception.Message -match 'TasksOperationsNotAllowed') {
      throw "ACR Tasks are not permitted for '$AcrName' in subscription '$SubscriptionId'. This blocks 'az acr build'. You will need to (1) request enabling ACR Tasks / remove policy restriction, or (2) build images elsewhere (e.g., GitHub Actions) and push to ACR. Original error: $($_.Exception.Message)"
    }
    throw
  }
} else {
  Write-Host "Base image already exists in ACR; skipping base rebuild: $fullBaseImageName" -ForegroundColor Green
}

Write-Host "Building + pushing APP image (delta) to ACR: $($ImageRepository):$Tag"
try {
  Invoke-Az -Args @(
    'acr','build',
    '-g',$ResourceGroup,
    '-r',$AcrName,
    '-t',"$($ImageRepository):$Tag",
    '--build-arg',("BASE_IMAGE={0}" -f $fullBaseImageName),
    '-f','Dockerfile','.'
  )
} catch {
  if ($_.Exception.Message -match 'TasksOperationsNotAllowed') {
    throw "ACR Tasks are not permitted for '$AcrName' in subscription '$SubscriptionId'. This blocks 'az acr build'. You will need to (1) request enabling ACR Tasks / remove policy restriction, or (2) build images elsewhere (e.g., GitHub Actions) and push to ACR. Original error: $($_.Exception.Message)"
  }
  throw
}

Write-Host "Build/push complete. App Service update skipped (by design)." -ForegroundColor Green
Write-Host "App image:  $fullImageName"
Write-Host "Base image: $fullBaseImageName"

Write-Host "Restarting web app..."
Invoke-Az -Args @('webapp','restart','-g',$ResourceGroup,'-n',$WebAppName,'-o','none') | Out-Null
Write-Host "Restart requested." -ForegroundColor Green
