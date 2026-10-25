param([string]$DryRun = '0', [string]$NextVersion = '', [string]$SkipValidation = '0')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')
$arguments = @('run', '--no-project', '--python', '3.13', 'python', 'scripts/release.py')
if ($DryRun -match '^(1|true|yes)$') { $arguments += '--dry-run' }
if ($SkipValidation -match '^(1|true|yes)$') { $arguments += '--skip-validation' }
if ($NextVersion) { $arguments += @('--next-version', $NextVersion) }
& uv @arguments
if ($LASTEXITCODE -ne 0) { throw 'Release preparation failed.' }
