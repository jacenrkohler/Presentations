#!/usr/bin/env bash
# LAB1-4_Windows_pre-fetch.sh - download every file that Labs 1 to 4 needs on Windows, so that the lab runs without the internet.
#
# The files go into the download folder (Downloads/Windows next to the lab folders, or the USB folder that holds
# this Ai-workshop folder). Then follow the ..._OFFLINE.md walkthrough. The script can run on any operating system
# with Bash (Windows: Git Bash or WSL). It needs curl, Python 3 with pip (3.8 or newer), and Docker for the
# Docker images and the Ollama models.
#     bash LAB1-4_Windows_pre-fetch.sh
# Options:
#     --dry-run      show what is present and what is missing, download nothing
#     --optional     also the optional files (Ministral 3, image models)
#     --gpu          also the NVIDIA GPU files, into the folder gpu (not for macOS: the normal files use Metal)
#     --skip-docker  do not save the Docker images or the Ollama models
#     --refresh      ask pip again for the newest Python packages
#     --dest DIR     use DIR as the download folder
#     --pack         also copy the lab files (Labs 1 to 5) into <download folder>/Ai-workshop
#     --pack-only    only copy the lab files, download nothing
# The script examines each file before it downloads it. Files that are present are skipped. It downloads one file at
# a time and keeps partial files, so if the connection stops, run it again: it continues where it stopped.
# The same script is also in Python (.py) and PowerShell (.ps1). They do the same work.
set -u
OS_NAME="Windows"
LABS="1234"
ROOT_UP=0
SCOPE="Labs 1 to 4"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$ROOT_UP" = 1 ]; then ROOT="$(cd "$HERE/.." && pwd)"; else ROOT="$HERE"; fi
DRY=0; OPTIONAL=0; GPU=0; SKIP_DOCKER=0; REFRESH=0; PACK=0; PACK_ONLY=0; DEST=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;; --optional) OPTIONAL=1 ;; --gpu) GPU=1 ;; --skip-docker) SKIP_DOCKER=1 ;; --refresh) REFRESH=1 ;;
    --pack) [ ${#LABS} -gt 1 ] && PACK=1 || { echo "--pack is only for the Download All script"; exit 2; } ;;
    --pack-only) [ ${#LABS} -gt 1 ] && { PACK=1; PACK_ONLY=1; } || { echo "--pack-only is only for the Download All script"; exit 2; } ;;
    --dest) shift; DEST="${1:-}" ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown option: $1 (use --help)"; exit 2 ;;
  esac
  shift
done
if [ -z "$DEST" ]; then
  PARENT="$(dirname "$ROOT")"
  if [ "$(basename "$PARENT")" = "$OS_NAME" ]; then DEST="$PARENT"; else DEST="$ROOT/Downloads/$OS_NAME"; fi
fi
mkdir -p "$DEST" && DEST="$(cd "$DEST" && pwd)"
PY="${PYTHON:-}"
if [ -z "$PY" ]; then for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done; fi
FAILS=()
PIP_SHIM='import sys,runpy; import pip._vendor.packaging.markers as m; o=m.default_environment; t=dict(x.split('\''='\'',1) for x in sys.argv[1].split('\'';'\'')); m.default_environment=lambda: dict(o(), **t); sys.argv=['\''pip'\'']+sys.argv[2:]; runpy.run_module('\''pip'\'', run_name='\''__main__'\'', alter_sys=True)'
PIP_ENV="os_name=nt;sys_platform=win32;platform_system=Windows;platform_machine=AMD64"

# group|labs|relative path|URL
FILES=(
  "base|1234|python-3.12.10-amd64.exe|https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
  "base|124|wsl.3.0.3.0.x64.msi|https://github.com/microsoft/WSL/releases/download/3.0.3/wsl.3.0.3.0.x64.msi"
  "base|124|Docker Desktop Installer.exe|https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
  "base|3|VSCodeUserSetup-x64.exe|https://update.code.visualstudio.com/latest/win32-x64-user/stable"
  "base|3|continue-win32-x64-1.3.40.vsix|https://github.com/continuedev/continue/releases/download/v1.3.40-vscode/continue-win32-x64-1.3.40.vsix"
  "base|3|Obsidian-1.15.0.exe|https://github.com/obsidianmd/obsidian-releases/releases/download/v1.15.0/Obsidian-1.15.0.exe"
  "base|1|koboldcpp-nocuda.exe|https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp-nocuda.exe"
  "base|1234|llama_cpp_python-0.3.36-py3-none-win_amd64.whl|https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36/llama_cpp_python-0.3.36-py3-none-win_amd64.whl"
  "gpu|1|gpu/koboldcpp.exe|https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp.exe"
  "gpu|1234|gpu/llama_cpp_python-0.3.36-py3-none-win_amd64.whl|https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36-cu124/llama_cpp_python-0.3.36-py3-none-win_amd64.whl"
  "base|1234|qwen2.5-1.5b-instruct-q4_k_m.gguf|https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
  "base|1234|Qwen3-4B-Q4_K_M.gguf|https://huggingface.co/ggml-org/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf"
  "base|123|qwen2.5-0.5b-instruct/config.json|https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
  "base|123|qwen2.5-0.5b-instruct/generation_config.json|https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
  "base|123|qwen2.5-0.5b-instruct/tokenizer.json|https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
  "base|123|qwen2.5-0.5b-instruct/tokenizer_config.json|https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
  "base|123|qwen2.5-0.5b-instruct/model.safetensors|https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors"
  "base|1234|qwen2.5-0.5b-instruct-onnx/config.json|https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
  "base|1234|qwen2.5-0.5b-instruct-onnx/generation_config.json|https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
  "base|1234|qwen2.5-0.5b-instruct-onnx/tokenizer.json|https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
  "base|1234|qwen2.5-0.5b-instruct-onnx/tokenizer_config.json|https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
  "base|1234|qwen2.5-0.5b-instruct-onnx/onnx/model_quantized.onnx|https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/onnx/model_quantized.onnx"
  "optional|12|Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf|https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf"
  "optional|12|Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf|https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf"
  "optional|1|vit-base-patch16-224/config.json|https://huggingface.co/google/vit-base-patch16-224/resolve/main/config.json"
  "optional|1|vit-base-patch16-224/preprocessor_config.json|https://huggingface.co/google/vit-base-patch16-224/resolve/main/preprocessor_config.json"
  "optional|1|vit-base-patch16-224/model.safetensors|https://huggingface.co/google/vit-base-patch16-224/resolve/main/model.safetensors"
  "optional|1|sd-turbo/model_index.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/model_index.json"
  "optional|1|sd-turbo/scheduler/scheduler_config.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/scheduler/scheduler_config.json"
  "optional|1|sd-turbo/text_encoder/config.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/config.json"
  "optional|1|sd-turbo/text_encoder/model.fp16.safetensors|https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/model.fp16.safetensors"
  "optional|1|sd-turbo/tokenizer/merges.txt|https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/merges.txt"
  "optional|1|sd-turbo/tokenizer/special_tokens_map.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/special_tokens_map.json"
  "optional|1|sd-turbo/tokenizer/tokenizer_config.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/tokenizer_config.json"
  "optional|1|sd-turbo/tokenizer/vocab.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/vocab.json"
  "optional|1|sd-turbo/unet/config.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/config.json"
  "optional|1|sd-turbo/unet/diffusion_pytorch_model.fp16.safetensors|https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors"
  "optional|1|sd-turbo/vae/config.json|https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/config.json"
  "optional|1|sd-turbo/vae/diffusion_pytorch_model.fp16.safetensors|https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/diffusion_pytorch_model.fp16.safetensors"
)
# group|labs|index page|regex (the newest version is used)
INDEX_FILES=(

)
PLATFORM=("win_amd64")
# group|labs|name|folder|index URLs (space separated, PYPI = the normal index)|no-deps (0/1)|packages
PIP=(
  "base|1234|core|.|PYPI|0|gguf numpy safetensors onnx onnxruntime transformers jinja2 diskcache typing-extensions"
  "base|123|hf|.|PYPI|0|diffusers pillow transformers psutil pyyaml packaging huggingface_hub sympy networkx fsspec filelock setuptools mpmath jinja2 typing-extensions numpy safetensors"
  "base|123|accelerate|.|PYPI|1|accelerate"
  "base|123|torch|.|PYPI|1|torch"
  "gpu|123|torch-cuda|gpu|https://download.pytorch.org/whl/cu128 https://download.pytorch.org/whl/cu126|0|torch"
  "gpu|1234|onnxruntime-gpu|gpu|PYPI|0|onnxruntime-gpu"
)
# labs|packages that pip must find offline
CHECKS=(
  "1234|llama-cpp-python gguf numpy safetensors onnx onnxruntime transformers jinja2 diskcache typing-extensions"
  "123|torch transformers accelerate diffusers pillow"
)
# group|labs|image|platform|folder
IMAGES=(
  "base|12|ollama/ollama:latest|linux/amd64|."
  "base|124|ghcr.io/open-webui/open-webui:main|linux/amd64|."
  "base|12|koboldai/koboldcpp:latest|linux/amd64|."
  "base|12|ghcr.io/ggml-org/llama.cpp:server|linux/amd64|."
  "gpu|12|ghcr.io/ggml-org/llama.cpp:server-cuda|linux/amd64|gpu"
)
# group|labs|model
OLLAMA=(
  "base|12|qwen2.5:1.5b"
  "base|2|qwen3:1.7b"
)
PACK_DIRS=("Lab01" "Lab02" "Lab03" "Lab04" "Lab05" "prefetch" "Memes")
PACK_SKIP_FILES=("BONUS-LABS-PASSWORD.md" "INSTRUCTOR-GUIDE-Lab05.md" "TODO.md" "InstructorNotes.md" "deck-source.zip" "compose.yaml.new")
PACK_SKIP_DIRS=(".venv" "__pycache__" ".git" "Lab01/models" "Lab01/kobold" "Lab01/prefetch" "Lab01/logs" "logs" "results")
PACK_SKIP_EXT=(".gguf" ".part" ".zip")

in_labs() { local i; for ((i = 0; i < ${#1}; i++)); do case "$LABS" in *"${1:$i:1}"*) return 0 ;; esac; done; return 1; }
want() {  # want <group> <labs>
  in_labs "$2" || return 1
  case "$1" in base) return 0 ;; optional) [ "$OPTIONAL" = 1 ] ;; gpu) [ "$GPU" = 1 ] && [ "$OS_NAME" != MacOS ] ;; *) return 1 ;; esac
}
sha_of() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

get() {  # get <relative path> <URL> [sha256]
  local rel="$1" url="$2" sha="${3:-}" dest="$DEST/$1" try
  if [ -s "$dest" ]; then echo "  present  $rel"; return 0; fi
  if [ "$DRY" = 1 ]; then echo "  MISSING  $rel"; return 0; fi
  mkdir -p "$(dirname "$dest")"
  for try in 1 2 3; do
    if curl -fL --retry 2 --connect-timeout 30 -C - -A "bsides-workshop-fetch/2.0" -sS -o "$dest.part" "$url"; then
      if [ -n "$sha" ] && [ "$(sha_of "$dest.part")" != "$sha" ]; then
        rm -f "$dest.part"; echo "  retry $try: $rel: the sha256 checksum does not match"; continue
      fi
      mv -f "$dest.part" "$dest"; echo "  got      $rel ($(du -h "$dest" | cut -f1))"; return 0
    fi
    echo "  retry $try: $rel"
  done
  FAILS+=("$rel"); echo "  FAILED   $rel"; return 1
}

get_index() {  # get_index <page> <regex>
  local page="$1" rx="$2" f ver name
  for f in "$DEST"/*; do
    [ -f "$f" ] || continue
    if "$PY" -c 'import re,sys; sys.exit(0 if re.fullmatch(sys.argv[1], sys.argv[2]) else 1)' "$rx" "$(basename "$f")"; then
      echo "  present  $(basename "$f")"; return 0
    fi
  done
  if [ "$DRY" = 1 ]; then echo "  MISSING  $rx (newest from $page)"; return 0; fi
  ver="$(curl -fsSL "$page" | "$PY" -c 'import re,sys; v=set(re.findall(sys.argv[1], sys.stdin.read())); print(max(v, key=lambda s: [int(x) for x in s.split(".")]) if v else "")' "$rx")"
  if [ -z "$ver" ]; then FAILS+=("$page"); echo "  FAILED   $page"; return 1; fi
  name="$("$PY" -c 'import sys; print(sys.argv[1].replace(r"([0-9]+\.[0-9]+\.[0-9]+)", sys.argv[2]).replace("\\", ""))' "$rx" "$ver")"
  get "$name" "$page$name"
}

pip_base() {  # prints the shared pip arguments, one per line
  printf '%s\n' -c "$PIP_SHIM" "$PIP_ENV" install --dry-run --ignore-installed --quiet --disable-pip-version-check --only-binary=:all: \
    --python-version 3.12 --implementation cp --abi cp312
  local p; for p in "${PLATFORM[@]}"; do printf '%s\n' --platform "$p"; done
}

pip_set() {  # pip_set <name> <folder> <indexes> <no-deps> <packages>
  local name="$1" folder="$2" idx="$3" nd="$4" pkgs="$5" cache="$DEST/.prefetch/$OS_NAME-$1.tsv" i tmp ok=0 fn url sha
  local base=(); while IFS= read -r line; do base+=("$line"); done < <(pip_base)
  if [ "$REFRESH" = 1 ] || [ ! -f "$cache" ]; then
    if [ "$DRY" = 1 ]; then echo "  MISSING  Python package set '$name' (the list comes from pip when you run without --dry-run)"; return 0; fi
    echo "  asking pip for the files of '$name' ..."
    mkdir -p "$DEST/.prefetch"
    for i in $idx; do
      tmp="$(mktemp -d)"
      local extra=(); [ "$nd" = 1 ] && extra+=(--no-deps); [ "$i" != PYPI ] && extra+=(--index-url "$i")
      if "$PY" "${base[@]}" --target "$tmp/t" --report "$tmp/r.json" ${extra[@]+"${extra[@]}"} $pkgs; then
        "$PY" -c '
import json, sys, urllib.parse
rows = []
for it in json.load(open(sys.argv[1], encoding="utf-8"))["install"]:
    d = it["download_info"]
    fn = urllib.parse.unquote(d["url"].split("/")[-1].split("#")[0])
    rows.append("\t".join([fn, d["url"], (d.get("archive_info", {}).get("hashes") or {}).get("sha256", "")]))
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(rows) + "\n")' "$tmp/r.json" "$cache" && ok=1
      fi
      rm -rf "$tmp"
      [ "$ok" = 1 ] && break
    done
    if [ "$ok" = 0 ]; then FAILS+=("pip set $name"); echo "  FAILED   pip set $name"; return 1; fi
  fi
  while IFS=$'\t' read -r fn url sha; do
    if [ -n "$fn" ]; then if [ "$folder" = . ]; then get "$fn" "$url" "$sha"; else get "$folder/$fn" "$url" "$sha"; fi; fi
  done < "$cache"
}

pip_check() {  # pip_check <packages>
  local base=() tmp out; while IFS= read -r line; do base+=("$line"); done < <(pip_base)
  tmp="$(mktemp -d)"
  if out="$("$PY" "${base[@]}" --target "$tmp/t" --no-index --find-links "$DEST" $1 2>&1)"; then
    echo "  OK       pip finds $1 and all their dependencies offline"
  else
    FAILS+=("offline pip check"); echo "  FAILED   offline pip check: $(echo "$out" | tail -2 | tr '\n' ' ')"
  fi
  rm -rf "$tmp"
}

run() { echo "   \$ $*"; "$@"; }

docker_items() {
  local e g labs img plat folder name dest model n tag todo=() store="$DEST/ollama"
  if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
    for e in "${IMAGES[@]}"; do IFS='|' read -r g labs img plat folder <<<"$e"
      if want "$g" "$labs"; then FAILS+=("docker"); echo "  Docker is not installed or not running: Docker images and Ollama models skipped."; return; fi
    done
    return
  fi
  for e in "${IMAGES[@]}"; do
    IFS='|' read -r g labs img plat folder <<<"$e"; want "$g" "$labs" || continue
    name="$(echo "$img" | tr '/:' '__')_${plat#*/}.tar"; dest="$DEST/$folder/$name"
    if [ -f "$dest" ]; then echo "  present  $name"; continue; fi
    if [ "$DRY" = 1 ]; then echo "  MISSING  $name"; continue; fi
    mkdir -p "$DEST/$folder"
    if run docker pull --platform "$plat" "$img" && run docker save -o "$dest.part" "$img"; then mv -f "$dest.part" "$dest"
    else FAILS+=("$name"); fi
  done
  for e in "${OLLAMA[@]}"; do
    IFS='|' read -r g labs model <<<"$e"; want "$g" "$labs" || continue
    n="${model%%:*}"; tag="${model#*:}"; [ "$tag" = "$model" ] && tag=latest
    if [ -f "$store/models/manifests/registry.ollama.ai/library/$n/$tag" ]; then echo "  present  ollama model $model"
    elif [ "$DRY" = 1 ]; then echo "  MISSING  ollama model $model"
    else todo+=("$model"); fi
  done
  if [ "${#todo[@]}" -gt 0 ]; then
    mkdir -p "$store"; docker rm -f ws-fetch-ollama >/dev/null 2>&1
    if run docker run -d --name ws-fetch-ollama -v "$store:/root/.ollama" ollama/ollama:latest; then
      for model in "${todo[@]}"; do run docker exec ws-fetch-ollama ollama pull "$model" || FAILS+=("ollama $model"); done
      docker exec ws-fetch-ollama chmod -R a+rwX /root/.ollama >/dev/null 2>&1
    else FAILS+=("ollama models"); fi
    docker rm -f ws-fetch-ollama >/dev/null 2>&1
  fi
}

skip_file() {
  local f="$1" s
  for s in "${PACK_SKIP_FILES[@]}"; do [ "$f" = "$s" ] && return 0; done
  for s in "${PACK_SKIP_EXT[@]}"; do case "$f" in *"$s") return 0 ;; esac; done
  return 1
}

pack() {
  local dest="$DEST/Ai-workshop" n=0 f top rel d s prune
  if [ -d "$dest" ] && [ "$(cd "$dest" && pwd)" = "$ROOT" ]; then echo "  The lab files are already in the download folder."; return; fi
  echo "Lab files -> $dest"
  [ "$DRY" = 1 ] && return
  mkdir -p "$dest"
  for f in "$ROOT"/* "$ROOT"/.[!.]*; do
    [ -f "$f" ] || continue
    skip_file "$(basename "$f")" && continue
    cp -p "$f" "$dest/"; n=$((n + 1))
  done
  for top in "${PACK_DIRS[@]}"; do
    [ -d "$ROOT/$top" ] || continue
    while IFS= read -r -d '' f; do
      rel="${f#"$ROOT"/}"; prune=0
      for s in "${PACK_SKIP_DIRS[@]}"; do
        case "$s" in
          */*) case "$rel" in "$s"/*) prune=1 ;; esac ;;
          *) case "/$rel" in */"$s"/*) prune=1 ;; esac ;;
        esac
      done
      [ "$prune" = 1 ] && continue
      skip_file "$(basename "$f")" && continue
      d="$dest/$(dirname "$rel")"; mkdir -p "$d"; cp -p "$f" "$d/"; n=$((n + 1))
    done < <(find "$ROOT/$top" -type f -print0)
  done
  echo "  copied $n files"
}

echo "$SCOPE, $OS_NAME: download folder $DEST$([ "$DRY" = 1 ] && echo '  (dry run)')"
if [ -z "$PY" ]; then echo "Python 3 is not installed. Install Python 3.12 first (see the pre-work file)."; exit 1; fi
if [ "$GPU" = 1 ] && [ "$OS_NAME" = MacOS ]; then echo "macOS: the normal files use the Apple GPU (Metal). --gpu adds nothing."; fi

if [ "$PACK_ONLY" = 0 ]; then
  echo "Files (installers, programs, models):"
  for e in "${FILES[@]}"; do IFS='|' read -r g labs rel url <<<"$e"; want "$g" "$labs" && get "$rel" "$url"; done
  for e in ${INDEX_FILES[@]+"${INDEX_FILES[@]}"}; do IFS='|' read -r g labs page rx <<<"$e"; want "$g" "$labs" && get_index "$page" "$rx"; done
  echo "Python packages for Python 3.12 (one file at a time):"
  for e in "${PIP[@]}"; do IFS='|' read -r g labs name folder idx nd pkgs <<<"$e"; want "$g" "$labs" && pip_set "$name" "$folder" "$idx" "$nd" "$pkgs"; done
  if [ "$SKIP_DOCKER" = 0 ]; then echo "Docker images and Ollama models:"; docker_items; fi
  if [ "$DRY" = 0 ]; then
    echo "Offline check of the Python packages:"
    for e in "${CHECKS[@]}"; do IFS='|' read -r labs pkgs <<<"$e"; in_labs "$labs" && pip_check "$pkgs"; done
  fi
fi
[ "$PACK" = 1 ] && pack
echo
if [ "$DRY" = 1 ]; then echo "Dry run: nothing was downloaded."; exit 0; fi
if [ "${#FAILS[@]}" -gt 0 ]; then echo "Not complete. Failed: ${FAILS[*]}"; echo "Run the script again. It continues where it stopped."; exit 1; fi
echo "Complete. Everything for $SCOPE is in $DEST"
