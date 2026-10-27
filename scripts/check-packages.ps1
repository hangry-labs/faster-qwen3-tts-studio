$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')

# dist/ can retain earlier snapshots. Validate the pair for this checkout rather
# than applying today's notice requirements to unrelated historical artifacts.
$projectJson = & uv run --no-project --python 3.13 python -c 'import json,re,tomllib; p=tomllib.load(open("pyproject.toml","rb"))["project"]; print(json.dumps({"name":re.sub(r"[-_.]+","_",p["name"]).lower(),"version":p["version"]}))'
if ($LASTEXITCODE -ne 0) { throw 'Could not read current package metadata.' }
$project = $projectJson | ConvertFrom-Json
$stem = "$($project.name)-$($project.version)"
$artifacts = @("dist/$stem-py3-none-any.whl", "dist/$stem.tar.gz" | ForEach-Object {
    if (!(Test-Path -LiteralPath $_ -PathType Leaf)) {
        throw "Missing current artifact: $_. Build both distributions with uv build first."
    }
    Get-Item -LiteralPath $_
})
$checkArgs = @('run', '--no-project', '--python', '3.13', 'python', 'scripts/check_licensing.py')
foreach ($artifact in $artifacts) { $checkArgs += @('--artifact', $artifact.FullName) }
& uv @checkArgs
if ($LASTEXITCODE -ne 0) { throw 'Distribution notice checks failed.' }
& uvx twine check --strict @($artifacts.FullName)
if ($LASTEXITCODE -ne 0) { throw 'Distribution metadata checks failed.' }
Write-Host 'Local Python artifacts are ready in dist/. This task does not publish them.'
