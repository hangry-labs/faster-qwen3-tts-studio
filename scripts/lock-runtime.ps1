param([string]$Check = '0')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')
$lockPath = 'requirements.runtime.txt'
$arguments = @('pip', 'compile', 'requirements.runtime.in', '--python-version', '3.13',
    '--python-platform', 'x86_64-manylinux_2_28', '--index-strategy', 'unsafe-best-match',
    '--generate-hashes', '--no-header', '--no-annotate', '--emit-index-url')
if ($Check -match '^(1|true|yes)$') {
    $temporary = [IO.Path]::GetTempFileName()
    try {
        & uv @arguments '--constraint' $lockPath '--output-file' $temporary
        if ($LASTEXITCODE -ne 0) { throw 'Existing runtime lock does not satisfy the inputs.' }
        $before = (Get-Content -LiteralPath $lockPath -Raw).Replace("`r`n", "`n")
        $after = (Get-Content -LiteralPath $temporary -Raw).Replace("`r`n", "`n")
        if ($before -ne $after) { throw 'Runtime lock is stale. Regenerate it with task lock-runtime.' }
    } finally { Remove-Item -LiteralPath $temporary -ErrorAction SilentlyContinue }
} else {
    & uv @arguments '--output-file' $lockPath
    if ($LASTEXITCODE -ne 0) { throw 'Runtime lock compilation failed.' }
}
