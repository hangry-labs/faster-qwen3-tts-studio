param(
    [string]$Models = 'all',
    [ValidateRange(1, 10)][int]$Repeats = 2,
    [string]$Output = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Set-Location -LiteralPath $repoRoot
$image = if ($env:QWEN_TASK_IMAGE) { $env:QWEN_TASK_IMAGE } else { 'faster-qwen3-tts-studio:dev' }
$volume = if ($env:QWEN_TASK_DATA_VOLUME) { $env:QWEN_TASK_DATA_VOLUME } else { 'faster_qwen3_tts_studio_data' }
$container = if ($env:QWEN_TASK_CONTAINER) { $env:QWEN_TASK_CONTAINER } else { 'faster-qwen3-tts-studio' }
$gpu = if ($env:QWEN_TASK_GPU_DEVICE) { $env:QWEN_TASK_GPU_DEVICE } else { '0' }
$running = & docker ps --filter "name=^/$container`$" --format '{{.Names}}'
if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect Docker.' }
if ($running) { throw 'Stop the Studio before benchmarking to free its resident model memory. Restart it after the benchmark.' }
$activeBenchmarks = & docker ps --filter 'label=app.hangrylabs.benchmark=faster-qwen3-tts-studio' --format '{{.Names}}'
if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect existing benchmarks.' }
if ($activeBenchmarks) { throw 'Another project benchmark is running. Finish it before starting a decoder comparison.' }
if (!$Output) { $Output = Join-Path $repoRoot ('benchmark-artifacts/decoder-context/' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
$outputPath = [System.IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$runArgs = @('run', '--rm', '--gpus', "device=$gpu", '--network', 'none',
    '--label', 'app.hangrylabs.benchmark=faster-qwen3-tts-studio',
    '--mount', "type=volume,source=$volume,target=/models,readonly",
    '--mount', "type=bind,source=$repoRoot/benchmarks,target=/app/benchmarks,readonly",
    '--mount', "type=bind,source=$outputPath,target=/results",
    '-e', 'HF_HOME=/models/huggingface', '-e', 'HF_HUB_OFFLINE=1',
    '-e', 'TRANSFORMERS_OFFLINE=1', '-e', 'PYTHONDONTWRITEBYTECODE=1',
    '-e', 'TORCHINDUCTOR_CACHE_DIR=/tmp/torch_inductor',
    $image, 'python', '-m', 'benchmarks.decoder_context', '--output', '/results',
    '--models', $Models, '--repeats', "$Repeats")
& docker @runArgs
if ($LASTEXITCODE -ne 0) { throw "Decoder-context benchmark failed. Retained evidence: $outputPath" }
Write-Host "Decoder-context results: $outputPath/RESULTS.md"
