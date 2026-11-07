<#
LAB04_Windows_pre-fetch.ps1 - download every file that Lab 4 (Logging and Compliance) needs on Windows, so that the lab runs without the internet.

The files go into the download folder (Downloads\Windows next to the lab folders, or the USB folder that holds
this Ai-workshop folder). Then follow the ..._OFFLINE.md walkthrough. The script can run on any operating system
with Windows PowerShell 5.1 or PowerShell 7 (pwsh). It needs Python 3 with pip (3.8 or newer), and Docker for the
Docker images and the Ollama models.
    powershell -ExecutionPolicy Bypass -File .\LAB04_Windows_pre-fetch.ps1
Options (the Bash and Python spellings, for example --dry-run, also work):
    -DryRun      show what is present and what is missing, download nothing
    -Optional    also the optional files (Ministral 3, image models)
    -Gpu         also the NVIDIA GPU files, into the folder gpu (not for macOS: the normal files use Metal)
    -SkipDocker  do not save the Docker images or the Ollama models
    -Refresh     ask pip again for the newest Python packages
    -Dest DIR    use DIR as the download folder
The script examines each file before it downloads it. Files that are present are skipped. It downloads one file at
a time and keeps partial files, so if the connection stops, run it again: it continues where it stopped.
The same script is also in Bash (.sh) and Python (.py). They do the same work.
#>
$OsName = "Windows"
$Labs = "4"
$RootUp = 1
$Scope = "Lab 4 (Logging and Compliance)"
$DryRun = $false; $Optional = $false; $Gpu = $false; $SkipDocker = $false; $Refresh = $false; $Pack = $false; $PackOnly = $false; $DlDir = $null
for ($i = 0; $i -lt $args.Count; $i++) {
    $a = [string]$args[$i]
    switch -regex ($a) {
        '^(-DryRun|--dry-run)$' { $DryRun = $true }
        '^--?optional$' { $Optional = $true }
        '^--?gpu$' { $Gpu = $true }
        '^(-SkipDocker|--skip-docker)$' { $SkipDocker = $true }
        '^--?refresh$' { $Refresh = $true }
        '^--?pack$' { if ($Labs.Length -gt 1) { $Pack = $true } else { Write-Host "-Pack is only for the Download All script"; exit 2 } }
        '^(-PackOnly|--pack-only)$' { if ($Labs.Length -gt 1) { $Pack = $true; $PackOnly = $true } else { Write-Host "-PackOnly is only for the Download All script"; exit 2 } }
        '^--?dest$' { $i++; $DlDir = [string]$args[$i] }
        '^(-h|--help|-\?)$' { Get-Content $MyInvocation.MyCommand.Path -TotalCount 21; exit 0 }
        default { Write-Host "Unknown option: $a (use --help)"; exit 2 }
    }
}
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = if ($RootUp -eq 1) { Split-Path -Parent $Here } else { $Here }
if (-not $DlDir) {
    $Parent = Split-Path -Parent $Root
    $DlDir = if ((Split-Path -Leaf $Parent) -eq $OsName) { $Parent } else { Join-Path (Join-Path $Root "Downloads") $OsName }
}
New-Item -ItemType Directory -Force -Path $DlDir | Out-Null
$DlDir = (Resolve-Path -LiteralPath $DlDir).Path
$Fails = New-Object System.Collections.ArrayList
$OnWindows = ($env:OS -eq "Windows_NT")
$Curl = if ($OnWindows) { "curl.exe" } else { "curl" }
$Py = $null; $PyArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $Py = "py"; $PyArgs = @("-3") }
else { foreach ($c in @("python3", "python")) { if (Get-Command $c -ErrorAction SilentlyContinue) { $Py = $c; break } } }

$PipShim = 'import sys,runpy; import pip._vendor.packaging.markers as m; o=m.default_environment; t=dict(x.split(''='',1) for x in sys.argv[1].split('';'')); m.default_environment=lambda: dict(o(), **t); sys.argv=[''pip'']+sys.argv[2:]; runpy.run_module(''pip'', run_name=''__main__'', alter_sys=True)'
$PipEnv = "os_name=nt;sys_platform=win32;platform_system=Windows;platform_machine=AMD64"
# group, labs, relative path, URL
$Files = @(
    ,@("base", "1234", "python-3.12.10-amd64.exe", "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe")
    ,@("base", "124", "wsl.3.0.3.0.x64.msi", "https://github.com/microsoft/WSL/releases/download/3.0.3/wsl.3.0.3.0.x64.msi")
    ,@("base", "124", "Docker Desktop Installer.exe", "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe")
    ,@("base", "3", "VSCodeUserSetup-x64.exe", "https://update.code.visualstudio.com/latest/win32-x64-user/stable")
    ,@("base", "3", "continue-win32-x64-1.3.40.vsix", "https://github.com/continuedev/continue/releases/download/v1.3.40-vscode/continue-win32-x64-1.3.40.vsix")
    ,@("base", "3", "Obsidian-1.15.0.exe", "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.15.0/Obsidian-1.15.0.exe")
    ,@("base", "1", "koboldcpp-nocuda.exe", "https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp-nocuda.exe")
    ,@("base", "1234", "llama_cpp_python-0.3.36-py3-none-win_amd64.whl", "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36/llama_cpp_python-0.3.36-py3-none-win_amd64.whl")
    ,@("gpu", "1", "gpu/koboldcpp.exe", "https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp.exe")
    ,@("gpu", "1234", "gpu/llama_cpp_python-0.3.36-py3-none-win_amd64.whl", "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36-cu124/llama_cpp_python-0.3.36-py3-none-win_amd64.whl")
    ,@("base", "1234", "qwen2.5-1.5b-instruct-q4_k_m.gguf", "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf")
    ,@("base", "1234", "Qwen3-4B-Q4_K_M.gguf", "https://huggingface.co/ggml-org/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf")
    ,@("base", "123", "qwen2.5-0.5b-instruct/config.json", "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/config.json")
    ,@("base", "123", "qwen2.5-0.5b-instruct/generation_config.json", "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json")
    ,@("base", "123", "qwen2.5-0.5b-instruct/tokenizer.json", "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json")
    ,@("base", "123", "qwen2.5-0.5b-instruct/tokenizer_config.json", "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json")
    ,@("base", "123", "qwen2.5-0.5b-instruct/model.safetensors", "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors")
    ,@("base", "1234", "qwen2.5-0.5b-instruct-onnx/config.json", "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/config.json")
    ,@("base", "1234", "qwen2.5-0.5b-instruct-onnx/generation_config.json", "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json")
    ,@("base", "1234", "qwen2.5-0.5b-instruct-onnx/tokenizer.json", "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json")
    ,@("base", "1234", "qwen2.5-0.5b-instruct-onnx/tokenizer_config.json", "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json")
    ,@("base", "1234", "qwen2.5-0.5b-instruct-onnx/onnx/model_quantized.onnx", "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/onnx/model_quantized.onnx")
    ,@("optional", "12", "Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf", "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf")
    ,@("optional", "12", "Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf", "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf")
    ,@("optional", "1", "vit-base-patch16-224/config.json", "https://huggingface.co/google/vit-base-patch16-224/resolve/main/config.json")
    ,@("optional", "1", "vit-base-patch16-224/preprocessor_config.json", "https://huggingface.co/google/vit-base-patch16-224/resolve/main/preprocessor_config.json")
    ,@("optional", "1", "vit-base-patch16-224/model.safetensors", "https://huggingface.co/google/vit-base-patch16-224/resolve/main/model.safetensors")
    ,@("optional", "1", "sd-turbo/model_index.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/model_index.json")
    ,@("optional", "1", "sd-turbo/scheduler/scheduler_config.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/scheduler/scheduler_config.json")
    ,@("optional", "1", "sd-turbo/text_encoder/config.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/config.json")
    ,@("optional", "1", "sd-turbo/text_encoder/model.fp16.safetensors", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/model.fp16.safetensors")
    ,@("optional", "1", "sd-turbo/tokenizer/merges.txt", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/merges.txt")
    ,@("optional", "1", "sd-turbo/tokenizer/special_tokens_map.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/special_tokens_map.json")
    ,@("optional", "1", "sd-turbo/tokenizer/tokenizer_config.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/tokenizer_config.json")
    ,@("optional", "1", "sd-turbo/tokenizer/vocab.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/vocab.json")
    ,@("optional", "1", "sd-turbo/unet/config.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/config.json")
    ,@("optional", "1", "sd-turbo/unet/diffusion_pytorch_model.fp16.safetensors", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors")
    ,@("optional", "1", "sd-turbo/vae/config.json", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/config.json")
    ,@("optional", "1", "sd-turbo/vae/diffusion_pytorch_model.fp16.safetensors", "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/diffusion_pytorch_model.fp16.safetensors")
)
# group, labs, index page, regex (the newest version is used)
$IndexFiles = @(

)
$Platform = @("win_amd64")
# group, labs, name, folder, index URLs ("" = the normal index), no-deps, packages
$Pip = @(
    ,@("base", "1234", "core", ".", @(""), $false, @("gguf", "numpy", "safetensors", "onnx", "onnxruntime", "transformers", "jinja2", "diskcache", "typing-extensions"))
    ,@("base", "123", "hf", ".", @(""), $false, @("diffusers", "pillow", "transformers", "psutil", "pyyaml", "packaging", "huggingface_hub", "sympy", "networkx", "fsspec", "filelock", "setuptools", "mpmath", "jinja2", "typing-extensions", "numpy", "safetensors"))
    ,@("base", "123", "accelerate", ".", @(""), $true, @("accelerate"))
    ,@("base", "123", "torch", ".", @(""), $true, @("torch"))
    ,@("gpu", "123", "torch-cuda", "gpu", @("https://download.pytorch.org/whl/cu128", "https://download.pytorch.org/whl/cu126"), $false, @("torch"))
    ,@("gpu", "1234", "onnxruntime-gpu", "gpu", @(""), $false, @("onnxruntime-gpu"))
)
# labs, packages that pip must find offline
$Checks = @(
    ,@("1234", @("llama-cpp-python", "gguf", "numpy", "safetensors", "onnx", "onnxruntime", "transformers", "jinja2", "diskcache", "typing-extensions"))
    ,@("123", @("torch", "transformers", "accelerate", "diffusers", "pillow"))
)
# group, labs, image, platform, folder
$Images = @(
    ,@("base", "12", "ollama/ollama:latest", "linux/amd64", ".")
    ,@("base", "124", "ghcr.io/open-webui/open-webui:main", "linux/amd64", ".")
    ,@("base", "12", "koboldai/koboldcpp:latest", "linux/amd64", ".")
    ,@("base", "12", "ghcr.io/ggml-org/llama.cpp:server", "linux/amd64", ".")
    ,@("gpu", "12", "ghcr.io/ggml-org/llama.cpp:server-cuda", "linux/amd64", "gpu")
)
# group, labs, model
$Ollama = @(
    ,@("base", "12", "qwen2.5:1.5b")
    ,@("base", "2", "qwen3:1.7b")
)
$PackDirs = @("Lab01", "Lab02", "Lab03", "Lab04", "Lab05", "prefetch", "Memes")
$PackSkipFiles = @("BONUS-LABS-PASSWORD.md", "INSTRUCTOR-GUIDE-Lab05.md", "TODO.md", "InstructorNotes.md", "deck-source.zip", "compose.yaml.new")
$PackSkipDirs = @(".venv", "__pycache__", ".git", "Lab01/models", "Lab01/kobold", "Lab01/prefetch", "Lab01/logs", "logs", "results")
$PackSkipExt = @(".gguf", ".part", ".zip")

function In-Labs($l) { foreach ($ch in $l.ToCharArray()) { if ($Labs.Contains([string]$ch)) { return $true } }; return $false }
function Want($g, $l) {
    if (-not (In-Labs $l)) { return $false }
    return ($g -eq "base") -or ($g -eq "optional" -and $Optional) -or ($g -eq "gpu" -and $Gpu -and $OsName -ne "MacOS")
}
function Run([string[]]$cmd) {
    Write-Host ("   $ " + ($cmd -join " "))
    $exe = $cmd[0]; $rest = @(); if ($cmd.Count -gt 1) { $rest = $cmd[1..($cmd.Count - 1)] }
    & $exe @rest | Out-Host
    return ($LASTEXITCODE -eq 0)
}
function Get-One($rel, $url, $sha) {
    $dest = Join-Path $DlDir $rel
    if ((Test-Path -LiteralPath $dest) -and ((Get-Item -LiteralPath $dest).Length -gt 0)) { Write-Host "  present  $rel"; return }
    if ($DryRun) { Write-Host "  MISSING  $rel"; return }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
    for ($try = 1; $try -le 3; $try++) {
        & $Curl -fL --retry 2 --connect-timeout 30 -C - -A "bsides-workshop-fetch/2.0" -sS -o "$dest.part" $url | Out-Host
        if ($LASTEXITCODE -eq 0) {
            if ($sha -and ((Get-FileHash -Algorithm SHA256 -LiteralPath "$dest.part").Hash.ToLower() -ne $sha)) {
                Remove-Item -LiteralPath "$dest.part" -Force; Write-Host "  retry ${try}: ${rel}: the sha256 checksum does not match"; continue
            }
            Move-Item -Force -LiteralPath "$dest.part" -Destination $dest
            Write-Host ("  got      $rel ({0:N0} MB)" -f ((Get-Item -LiteralPath $dest).Length / 1MB)); return
        }
        Write-Host "  retry ${try}: ${rel}"
    }
    [void]$Fails.Add($rel); Write-Host "  FAILED   $rel"
}
function Get-Index($page, $rx) {
    foreach ($f in (Get-ChildItem -LiteralPath $DlDir -File -ErrorAction SilentlyContinue)) {
        if ($f.Name -match "^$rx$") { Write-Host "  present  $($f.Name)"; return }
    }
    if ($DryRun) { Write-Host "  MISSING  $rx (newest from $page)"; return }
    try {
        $html = (Invoke-WebRequest -UseBasicParsing -Uri $page -UserAgent "bsides-workshop-fetch/2.0").Content
        $vers = [regex]::Matches($html, $rx) | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique { [version]$_ }
        $ver = @($vers)[-1]
    } catch { $ver = $null }
    if (-not $ver) { [void]$Fails.Add($page); Write-Host "  FAILED   $page"; return }
    $name = $rx.Replace('([0-9]+\.[0-9]+\.[0-9]+)', $ver).Replace('\', '')
    Get-One $name ($page + $name) $null
}
function Pip-Base {
    $b = @() + $PyArgs + @("-c", $PipShim, $PipEnv, "install", "--dry-run", "--ignore-installed", "--quiet", "--disable-pip-version-check",
        "--only-binary=:all:", "--python-version", "3.12", "--implementation", "cp", "--abi", "cp312")
    foreach ($p in $Platform) { $b += @("--platform", $p) }
    return , $b
}
function New-TempDir { $t = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString()); New-Item -ItemType Directory -Path $t | Out-Null; return $t }
function Get-PipSet($name, $folder, $indexes, $noDeps, $pkgs) {
    $cacheDir = Join-Path $DlDir ".prefetch"; $cache = Join-Path $cacheDir "$OsName-$name.tsv"
    if ($Refresh -or -not (Test-Path -LiteralPath $cache)) {
        if ($DryRun) { Write-Host "  MISSING  Python package set '$name' (the list comes from pip when you run without -DryRun)"; return }
        Write-Host "  asking pip for the files of '$name' ..."
        New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
        $ok = $false
        foreach ($idx in $indexes) {
            $tmp = New-TempDir
            $cmd = @($Py) + (Pip-Base) + @("--target", (Join-Path $tmp "t"), "--report", (Join-Path $tmp "r.json"))
            if ($noDeps) { $cmd += "--no-deps" }
            if ($idx) { $cmd += @("--index-url", $idx) }
            $cmd += $pkgs
            if (Run $cmd) {
                $rep = Get-Content -Raw -Encoding UTF8 (Join-Path $tmp "r.json") | ConvertFrom-Json
                $rows = foreach ($it in $rep.install) {
                    $u = $it.download_info.url
                    $fn = [System.Uri]::UnescapeDataString(($u -split '#')[0].Split('/')[-1])
                    $h = ""; if ($it.download_info.archive_info -and $it.download_info.archive_info.hashes) { $h = [string]$it.download_info.archive_info.hashes.sha256 }
                    "$fn`t$u`t$h"
                }
                [System.IO.File]::WriteAllText($cache, (($rows -join "`n") + "`n"))
                $ok = $true
            }
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
            if ($ok) { break }
        }
        if (-not $ok) { [void]$Fails.Add("pip set $name"); Write-Host "  FAILED   pip set $name"; return }
    }
    foreach ($line in [System.IO.File]::ReadAllLines($cache)) {
        if (-not $line.Trim()) { continue }
        $p = $line.Split("`t")
        $rel = if ($folder -eq ".") { $p[0] } else { Join-Path $folder $p[0] }
        Get-One $rel $p[1] $(if ($p.Count -gt 2) { $p[2] } else { $null })
    }
}
function Pip-Check($pkgs) {
    $tmp = New-TempDir
    $cmd = @($Py) + (Pip-Base) + @("--target", (Join-Path $tmp "t"), "--no-index", "--find-links", $DlDir) + $pkgs
    $exe = $cmd[0]; $rest = $cmd[1..($cmd.Count - 1)]
    $out = & $exe @rest 2>&1 | Out-String
    $ok = ($LASTEXITCODE -eq 0)
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    if ($ok) { Write-Host "  OK       pip finds $($pkgs -join ' ') and all their dependencies offline" }
    else { [void]$Fails.Add("offline pip check"); Write-Host ("  FAILED   offline pip check: " + (($out.Trim() -split "`n") | Select-Object -Last 2) -join " ") }
}
function Docker-Items {
    $haveDocker = $false
    if (Get-Command docker -ErrorAction SilentlyContinue) { docker info *> $null; $haveDocker = ($LASTEXITCODE -eq 0) }
    if (-not $haveDocker) {
        foreach ($e in $Images) { if (Want $e[0] $e[1]) { [void]$Fails.Add("docker"); Write-Host "  Docker is not installed or not running: Docker images and Ollama models skipped."; return } }
        return
    }
    foreach ($e in $Images) {
        if (-not (Want $e[0] $e[1])) { continue }
        $img = $e[2]; $plat = $e[3]
        $name = ($img -replace '[/:]', '_') + "_" + $plat.Split("/")[1] + ".tar"
        $folder = if ($e[4] -eq ".") { $DlDir } else { Join-Path $DlDir $e[4] }
        $dest = Join-Path $folder $name
        if (Test-Path -LiteralPath $dest) { Write-Host "  present  $name"; continue }
        if ($DryRun) { Write-Host "  MISSING  $name"; continue }
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        if ((Run @("docker", "pull", "--platform", $plat, $img)) -and (Run @("docker", "save", "-o", "$dest.part", $img))) {
            Move-Item -Force -LiteralPath "$dest.part" -Destination $dest
        } else { [void]$Fails.Add($name) }
    }
    $store = Join-Path $DlDir "ollama"; $todo = @()
    foreach ($e in $Ollama) {
        if (-not (Want $e[0] $e[1])) { continue }
        $model = $e[2]; $n, $tag = $model.Split(":", 2); if (-not $tag) { $tag = "latest" }
        $man = Join-Path $store ("models/manifests/registry.ollama.ai/library/$n/$tag")
        if (Test-Path -LiteralPath $man) { Write-Host "  present  ollama model $model" }
        elseif ($DryRun) { Write-Host "  MISSING  ollama model $model" }
        else { $todo += $model }
    }
    if ($todo.Count -gt 0) {
        New-Item -ItemType Directory -Force -Path $store | Out-Null
        docker rm -f ws-fetch-ollama *> $null
        if (Run @("docker", "run", "-d", "--name", "ws-fetch-ollama", "-v", "${store}:/root/.ollama", "ollama/ollama:latest")) {
            foreach ($m in $todo) { if (-not (Run @("docker", "exec", "ws-fetch-ollama", "ollama", "pull", $m))) { [void]$Fails.Add("ollama $m") } }
            docker exec ws-fetch-ollama chmod -R a+rwX /root/.ollama *> $null
        } else { [void]$Fails.Add("ollama models") }
        docker rm -f ws-fetch-ollama *> $null
    }
}
function Skip-File($name) {
    if ($PackSkipFiles -contains $name) { return $true }
    foreach ($e in $PackSkipExt) { if ($name.EndsWith($e)) { return $true } }
    return $false
}
function Copy-Labs {
    $dest = Join-Path $DlDir "Ai-workshop"
    if ((Test-Path -LiteralPath $dest) -and ((Resolve-Path -LiteralPath $dest).Path -eq $Root)) { Write-Host "  The lab files are already in the download folder."; return }
    Write-Host "Lab files -> $dest"
    if ($DryRun) { return }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $n = 0
    foreach ($f in Get-ChildItem -LiteralPath $Root -File -Force) {
        if (Skip-File $f.Name) { continue }
        Copy-Item -LiteralPath $f.FullName -Destination $dest -Force; $n++
    }
    foreach ($top in $PackDirs) {
        $topPath = Join-Path $Root $top
        if (-not (Test-Path -LiteralPath $topPath)) { continue }
        foreach ($f in Get-ChildItem -LiteralPath $topPath -File -Recurse -Force) {
            $rel = $f.FullName.Substring($Root.Length + 1) -replace '\\', '/'
            $prune = $false
            foreach ($s in $PackSkipDirs) {
                if ($s.Contains("/")) { if ($rel.StartsWith("$s/")) { $prune = $true } }
                elseif (("/$rel").Contains("/$s/")) { $prune = $true }
            }
            if ($prune -or (Skip-File $f.Name)) { continue }
            $target = Join-Path $dest $rel
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $f.FullName -Destination $target -Force; $n++
        }
    }
    Write-Host "  copied $n files"
}

Write-Host ("$Scope, ${OsName}: download folder $DlDir" + $(if ($DryRun) { "  (dry run)" } else { "" }))
if (-not $Py) { Write-Host "Python 3 is not installed. Install Python 3.12 first (see the pre-work file)."; exit 1 }
if ($Gpu -and $OsName -eq "MacOS") { Write-Host "macOS: the normal files use the Apple GPU (Metal). -Gpu adds nothing." }

if (-not $PackOnly) {
    Write-Host "Files (installers, programs, models):"
    foreach ($e in $Files) { if (Want $e[0] $e[1]) { Get-One $e[2] $e[3] $null } }
    foreach ($e in $IndexFiles) { if ($e -and (Want $e[0] $e[1])) { Get-Index $e[2] $e[3] } }
    Write-Host "Python packages for Python 3.12 (one file at a time):"
    foreach ($e in $Pip) { if (Want $e[0] $e[1]) { Get-PipSet $e[2] $e[3] $e[4] $e[5] $e[6] } }
    if (-not $SkipDocker) { Write-Host "Docker images and Ollama models:"; Docker-Items }
    if (-not $DryRun) {
        Write-Host "Offline check of the Python packages:"
        foreach ($e in $Checks) { if (In-Labs $e[0]) { Pip-Check $e[1] } }
    }
}
if ($Pack) { Copy-Labs }
Write-Host ""
if ($DryRun) { Write-Host "Dry run: nothing was downloaded."; exit 0 }
if ($Fails.Count -gt 0) { Write-Host ("Not complete. Failed: " + ($Fails -join ", ")); Write-Host "Run the script again. It continues where it stopped."; exit 1 }
Write-Host "Complete. Everything for $Scope is in $DlDir"
