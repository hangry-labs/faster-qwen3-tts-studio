$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')

$artifacts = @(Get-ChildItem -LiteralPath 'dist' -File | Where-Object {
    $_.Name.EndsWith('.whl') -or $_.Name.EndsWith('.tar.gz')
})
if (!($artifacts | Where-Object Name -Like '*.whl') -or
    !($artifacts | Where-Object Name -Like '*.tar.gz')) {
    throw 'Build both a wheel and source distribution with uv build first.'
}
$checkArgs = @('run', '--no-project', '--python', '3.13', 'python', 'scripts/check_licensing.py')
foreach ($artifact in $artifacts) { $checkArgs += @('--artifact', $artifact.FullName) }
& uv @checkArgs
if ($LASTEXITCODE -ne 0) { throw 'Distribution notice checks failed.' }
& uvx twine check --strict @($artifacts.FullName)
if ($LASTEXITCODE -ne 0) { throw 'Distribution metadata checks failed.' }
Write-Host 'Local Python artifacts are ready in dist/. This task does not publish them.'
