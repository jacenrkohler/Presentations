#!/usr/bin/env python3
"""Lab 1, Part 1: look inside a model file.

A model file is a header (settings) plus a list of tensors (the weights). Three popular
formats store them in different ways:

  GGUF         one file, built for llama.cpp, Ollama and KoboldCpp. Often quantized (4-bit).
  safetensors  the Hugging Face format: a JSON header plus raw numbers, with config.json beside it.
  ONNX         a whole computation graph (operators plus weights), run by ONNX Runtime.

This tool reads all three and shows you the settings and the weights, as numbers, a histogram,
a picture, and a map. It never runs the model and never executes code from the file.

Setup:    python3 -m pip install -r requirements.txt

  python3 inspect_model.py summary MODEL            (a .gguf file, a .safetensors file or folder, or a .onnx file)
  python3 inspect_model.py tensor  MODEL NAME
  python3 inspect_model.py heatmap MODEL NAME --out q.png
  python3 inspect_model.py graph   MODEL --out model.html
  python3 inspect_model.py compare MODEL1 MODEL2 [MODEL3]
  python3 inspect_model.py scan    MODEL.bin         (old PyTorch pickle files: list what loading it would import)

For a node-and-edge view, try Netron:  python3 -m pip install netron   then   netron MODEL
"""
import argparse, glob, html, json, os, pickletools, re, struct, sys, zipfile, zlib
import numpy as np


# ---------------------------------------------------------------- reading
# Every format is turned into the same thing: a dict of settings ("meta") and a list of
# Tensor objects. A Tensor knows its name, shape, storage type and size, and can load its values.
class Tensor:
    def __init__(self, name, shape, dtype, n_bytes, loader):
        self.name, self.shape, self.dtype, self.n_bytes, self._loader = name, tuple(int(x) for x in shape), dtype, int(n_bytes), loader
        self.id = name  # the name stored in the file (ONNX may show a friendlier one)
        self.n_elements = int(np.prod(self.shape)) if self.shape else 1

    def values(self):
        return np.asarray(self._loader(), dtype=np.float32).reshape(self.shape)


class Model:
    def __init__(self, path, fmt, meta, tensors, notes=None):
        self.path, self.format, self.meta, self.tensors, self.notes = path, fmt, meta, tensors, notes or []


def detect(path):
    if os.path.isdir(path):
        if glob.glob(os.path.join(path, "*.safetensors")):
            return "safetensors"
        if glob.glob(os.path.join(path, "*.onnx")) or glob.glob(os.path.join(path, "onnx", "*.onnx")):
            return "onnx"
        if glob.glob(os.path.join(path, "*.gguf")):
            return "gguf"
        sys.exit(f"No .gguf, .safetensors or .onnx file found in {path}")
    if not os.path.exists(path):
        sys.exit(f"Not found: {path}. Run the prefetch script, or check the path.")
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        head = f.read(8)
    if head[:4] == b"GGUF":
        return "gguf"
    if ext == ".safetensors":
        return "safetensors"
    if ext == ".onnx":
        return "onnx"
    if ext in (".bin", ".pt", ".pth", ".ckpt", ".pkl") or head[:2] == b"PK" or head[:1] == b"\x80":
        sys.exit(f"{path} looks like a PyTorch pickle file. Loading one can run code hidden inside it.\n"
                 f"Do not load it. Run:  python3 inspect_model.py scan {path}")
    sys.exit(f"Unknown model format: {path}")


def load(path):
    return {"gguf": load_gguf, "safetensors": load_safetensors, "onnx": load_onnx}[detect(path)](path)


# ---- GGUF
def field_value(reader, key, default=None):
    f = reader.fields.get(key)
    if f is None:
        return default
    try:
        v = f.contents()
    except Exception:
        v = None
        try:
            last = f.parts[f.data[0]]
            v = bytes(last).decode("utf-8") if last.dtype == np.uint8 and len(last) > 1 else last[0].item()
        except Exception:
            return default
    if isinstance(v, (list, tuple)) and len(v) > 8:
        return len(v)  # long lists (the vocabulary): report how many
    return v


def load_gguf(path):
    try:
        import gguf
        from gguf import GGUFReader
    except ImportError:
        sys.exit("Install the gguf package: python3 -m pip install gguf")
    if os.path.isdir(path):
        path = sorted(glob.glob(os.path.join(path, "*.gguf")))[0]
    r = GGUFReader(path)
    arch = field_value(r, "general.architecture", "unknown")
    meta = {
        "name": field_value(r, "general.name", os.path.basename(path)),
        "architecture": arch,
        "layers": field_value(r, arch + ".block_count"),
        "embedding size": field_value(r, arch + ".embedding_length"),
        "feed-forward size": field_value(r, arch + ".feed_forward_length"),
        "attention heads": field_value(r, arch + ".attention.head_count"),
        "key/value heads": field_value(r, arch + ".attention.head_count_kv"),
        "head size": field_value(r, arch + ".attention.key_length"),
        "context length": field_value(r, arch + ".context_length"),
        "rope base": field_value(r, arch + ".rope.freq_base"),
        "vocabulary": field_value(r, "tokenizer.ggml.tokens"),
    }

    def loader(t):
        def f():
            qt = t.tensor_type
            if qt in (gguf.GGMLQuantizationType.F32, gguf.GGMLQuantizationType.F16, gguf.GGMLQuantizationType.BF16):
                return np.asarray(t.data).astype(np.float32)
            return gguf.quants.dequantize(t.data, qt)
        return f
    tensors = [Tensor(t.name, reversed(list(t.shape)), t.tensor_type.name, t.n_bytes, loader(t)) for t in r.tensors]
    notes = ["Quantized types (Q4_K, Q6_K, ...) store small blocks of integers plus a scale; the values shown are expanded back to floats."]
    return Model(path, "GGUF", meta, tensors, notes)


# ---- Hugging Face config.json (safetensors and ONNX exports both ship one)
def hf_meta(folder, default_name):
    cfg = {}
    for d in (folder, os.path.dirname(folder)):
        p = os.path.join(d, "config.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                cfg = json.load(f)
            break
    cfg = cfg.get("text_config", cfg)
    heads = cfg.get("num_attention_heads")
    hid = cfg.get("hidden_size")
    return {
        "name": cfg.get("_name_or_path") or default_name,
        "architecture": ", ".join(cfg.get("architectures", [])) or cfg.get("model_type", "unknown"),
        "layers": cfg.get("num_hidden_layers"),
        "embedding size": hid,
        "feed-forward size": cfg.get("intermediate_size"),
        "attention heads": heads,
        "key/value heads": cfg.get("num_key_value_heads", heads),
        "head size": cfg.get("head_dim") or (hid // heads if hid and heads else None),
        "context length": cfg.get("max_position_embeddings"),
        "rope base": cfg.get("rope_theta"),
        "vocabulary": cfg.get("vocab_size"),
        "stored as (config)": cfg.get("torch_dtype") or cfg.get("dtype"),
    }


# ---- safetensors: an 8-byte length, a JSON header, then raw numbers. Read directly, no torch.
ST_DTYPES = {"F64": (np.float64, 8), "F32": (np.float32, 4), "F16": (np.float16, 2), "BF16": (None, 2),
             "I64": (np.int64, 8), "I32": (np.int32, 4), "I16": (np.int16, 2), "I8": (np.int8, 1),
             "U8": (np.uint8, 1), "BOOL": (np.bool_, 1)}


def load_safetensors(path):
    folder = path if os.path.isdir(path) else os.path.dirname(path) or "."
    files = sorted(glob.glob(os.path.join(path, "*.safetensors"))) if os.path.isdir(path) else [path]
    tensors, extra = [], {}
    for fp in files:
        with open(fp, "rb") as f:
            n = struct.unpack("<Q", f.read(8))[0]
            header = json.loads(f.read(n))
        base = 8 + n
        extra.update(header.pop("__metadata__", {}) or {})
        for name, info in header.items():
            dt = info["dtype"]
            start, end = info["data_offsets"]

            def loader(fp=fp, dt=dt, off=base + start, count=end - start):
                raw = np.fromfile(fp, dtype=np.uint8, count=count, offset=off)
                if dt == "BF16":  # bfloat16 is the top half of a float32
                    return (raw.view(np.uint16).astype(np.uint32) << 16).view(np.float32)
                if dt not in ST_DTYPES:
                    sys.exit(f"Storage type {dt} is not supported by this tool.")
                return raw.view(ST_DTYPES[dt][0]).astype(np.float32)
            tensors.append(Tensor(name, info["shape"], dt, end - start, loader))
    meta = hf_meta(folder, os.path.basename(os.path.abspath(folder)))
    notes = ["safetensors holds only numbers and a JSON header, so opening it cannot run code. That is why it replaced pickle files."]
    if extra:
        notes.append("File metadata: " + json.dumps(extra)[:200])
    return Model(path, "safetensors", meta, tensors, notes)


# ---- ONNX: a graph of operators. The weights are the graph's "initializers".
def load_onnx(path):
    try:
        import onnx
        from onnx import numpy_helper
    except ImportError:
        sys.exit("Install the onnx package: python3 -m pip install onnx")
    if os.path.isdir(path):
        cands = sorted(glob.glob(os.path.join(path, "*.onnx")) + glob.glob(os.path.join(path, "onnx", "*.onnx")))
        path = cands[0]
    m = onnx.load(path, load_external_data=False)
    folder = os.path.dirname(os.path.abspath(path))
    # Exporters often rename weights (onnx::MatMul_123). Name each one after the graph node
    # that uses it, for example /model/layers.0/self_attn/q_proj/MatMul -> model.layers.0.self_attn.q_proj
    used_by = {}
    for node in m.graph.node:
        for inp in node.input:
            used_by.setdefault(inp, node.name)
    tensors = []
    for init in m.graph.initializer:
        dt = onnx.TensorProto.DataType.Name(init.data_type)
        n = int(np.prod(init.dims)) if init.dims else 1
        nbytes = len(init.raw_data) if init.raw_data else 0
        for kv in init.external_data:
            if kv.key == "length":
                nbytes = int(kv.value)
        if not nbytes:
            try:
                nbytes = n * np.dtype(onnx.helper.tensor_dtype_to_np_dtype(init.data_type)).itemsize
            except Exception:
                nbytes = n

        def loader(init=init):
            if init.data_location == onnx.TensorProto.EXTERNAL:
                onnx.external_data_helper.load_external_data_for_tensor(init, folder)
            return numpy_helper.to_array(init).astype(np.float32)
        t = Tensor(init.name, init.dims, dt, nbytes, loader)
        if not re.search(r"layers?\.\d+|embed|norm|lm_head", init.name) and used_by.get(init.name, "").startswith("/"):
            friendly = ".".join(p for p in used_by[init.name].strip("/").split("/")[:-1])
            suffix = re.search(r"_(quantized|scale|zero_point)$", init.name)
            t.name = friendly + (("." + suffix.group(1)) if suffix else ".weight") + "  [" + init.name + "]"
        tensors.append(t)
    ops = {}
    for node in m.graph.node:
        ops[node.op_type] = ops.get(node.op_type, 0) + 1
    meta = hf_meta(folder, os.path.basename(path))
    meta["graph operators"] = sum(ops.values())
    meta["graph inputs"] = len(m.graph.input)
    top = ", ".join("%s x%d" % kv for kv in sorted(ops.items(), key=lambda kv: -kv[1])[:8])
    notes = ["ONNX stores the whole computation as a graph. Most common operators: " + top,
             "Names like onnx::MatMul_123 are weights the exporter renamed while building the graph.",
             "Quantized ONNX models store weights as integers (INT8, UINT8, INT4) plus separate scale tensors."]
    return Model(path, "ONNX", meta, tensors, notes)


def shape_of(t):
    return t.shape


def type_name(t):
    return t.dtype


def values_of(t):
    """The weights as floats, whatever the storage type (quantized weights are expanded)."""
    return t.values()


def split_name(name):
    m = re.match(r"(?:.*?\.)?(?:blk|layers|h|layer)\.(\d+)\.(.+)", name)
    return (int(m.group(1)), m.group(2)) if m else (None, name)


def size_str(nbytes):
    return "%.2f GB" % (nbytes / 1e9) if nbytes >= 1e8 else "%.1f MB" % (nbytes / 1e6)


def human(n):
    for unit, k in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if n >= k:
            return "%.2f %s" % (n / k, unit)
    return str(int(n))


def kv_cache_bytes(meta, ctx):
    L, kv = meta["layers"], meta["key/value heads"] or meta["attention heads"]
    hs = meta["head size"] or ((meta["embedding size"] or 0) // max(meta["attention heads"] or 1, 1))
    if not (L and kv and hs):
        return 0
    return 2 * L * kv * hs * ctx * 2  # K and V, 2 bytes each (f16)


def groups(model):
    g = {"embedding": 0, "attention": 0, "feed-forward": 0, "norms": 0, "output": 0, "other": 0}
    for t in model.tensors:
        n = t.n_elements
        _, base = split_name(t.name)
        b = base.lower()
        if "embd" in b or "embed" in b or "wte" in b:
            g["embedding"] += n
        elif "norm" in b or "ln_" in b:
            g["norms"] += n
        elif b.startswith("output") or "lm_head" in b:
            g["output"] += n
        elif "attn" in b or "attention" in b or re.search(r"(^|\.)(q|k|v|o)_proj", b):
            g["attention"] += n
        elif "ffn" in b or "mlp" in b or re.search(r"(gate|up|down)_proj", b):
            g["feed-forward"] += n
        else:
            g["other"] += n
    return g


# ---------------------------------------------------------------- commands
def cmd_summary(a):
    r = load(a.model)
    meta = r.meta
    total = sum(int(t.n_elements) for t in r.tensors)
    size = sum(int(t.n_bytes) for t in r.tensors)
    print("Model: %s\nFormat: %s\n" % (meta["name"], r.format))
    for k, v in meta.items():
        if k != "name" and v is not None:
            print("  %-18s %s" % (k, v))
    print("\n  %-18s %s parameters in %d tensors" % ("size", human(total), len(r.tensors)))
    print("  %-18s %s on disk (about %.1f bits per weight)" % ("weights", size_str(size), 8.0 * size / max(total, 1)))
    kv = kv_cache_bytes(meta, a.ctx)
    print("  %-18s about %s with a %d-token context (weights plus the KV cache)" % ("memory to run", size_str(size + kv), a.ctx))
    print("  Leave room for your operating system: on a 16 GB laptop, keep the total under about 8 GB.\n")
    print("Where the parameters live:")
    for k, v in groups(r).items():
        if v:
            print("  %-14s %10s  %5.1f%%  %s" % (k, human(v), 100.0 * v / total, "#" * int(40 * v / total)))
    types = {}
    for t in r.tensors:
        types[type_name(t)] = types.get(type_name(t), 0) + 1
    print("\nStorage types: " + ", ".join("%s x%d" % kv_ for kv_ in sorted(types.items())))
    print("\nTensors outside the repeating blocks, then block 0 (every block has the same shapes):")
    show = [t for t in r.tensors if split_name(t.name)[0] in (None, 0)]
    w = min(max([28] + [len(t.name) for t in show]), 72)
    print("  %-*s %-18s %-7s %s" % (w, "name", "shape", "type", "parameters"))
    for t in show:
        print("  %-*s %-18s %-7s %s" % (w, t.name, "x".join(map(str, shape_of(t))) or "-", type_name(t), human(int(t.n_elements))))
    for n in r.notes:
        print("\nNote: " + n)
    first = next((t.id for t in r.tensors if ("attn_q" in t.name or "q_proj" in t.name) and len(t.shape) == 2), None) \
        or max(r.tensors, key=lambda t: t.n_elements).id
    print('\nNext: python3 inspect_model.py tensor %s "%s"' % (a.model, first))


def find_tensor(r, name):
    for t in r.tensors:
        if name in (t.name, t.id):
            return t
    close = [t.name for t in r.tensors if name in t.name][:8]
    sys.exit("No tensor named %r. %s" % (name, ("Did you mean: " + ", ".join(close)) if close else "Run summary to see names."))


def cmd_tensor(a):
    r = load(a.model)
    t = find_tensor(r, a.name)
    v = values_of(t)
    flat = v.reshape(-1)
    print("%s   shape %s   stored as %s   %s values" % (t.name, "x".join(map(str, v.shape)), type_name(t), human(flat.size)))
    print("min %.4f   max %.4f   mean %.5f   std %.4f   zeros %.2f%%\n" % (flat.min(), flat.max(), flat.mean(), flat.std(), 100.0 * (flat == 0).mean()))
    print("First %d values:" % a.count)
    print("  " + " ".join("%.4f" % x for x in flat[: a.count]))
    if v.ndim == 2:
        k = a.corner
        print("\nTop-left %dx%d corner (rows are outputs, columns are inputs):" % (min(k, v.shape[0]), min(k, v.shape[1])))
        for row in v[:k, :k]:
            print("  " + " ".join("%8.4f" % x for x in row))
    counts, edges = np.histogram(flat, bins=21, range=(float(np.percentile(flat, 0.5)), float(np.percentile(flat, 99.5))))
    peak = max(int(counts.max()), 1)
    print("\nHistogram (middle 99% of the values):")
    for c, lo in zip(counts, edges[:-1]):
        print("  %8.4f | %s" % (lo, "#" * int(50 * c / peak)))
    if re.match(r"U?INT", t.dtype):
        print("\nThese are stored integers, not the real weights. The real weight is about (value - zero_point) x scale,")
        print("using the matching _scale and _zero_point tensors. That is how 8-bit quantization saves space.")
    else:
        print("\nMost weights are small numbers near zero. Training moved every one of them a little at a time.")


def png_bytes(gray):
    h, w = gray.shape
    raw = b"".join(b"\x00" + gray[y].tobytes() for y in range(h))
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def cmd_heatmap(a):
    r = load(a.model)
    t = find_tensor(r, a.name)
    v = values_of(t)
    if v.ndim != 2:
        v = v.reshape(1, -1)
    v = v[: a.size, : a.size]
    lim = float(np.percentile(np.abs(v), 99)) or 1.0
    gray = ((np.clip(v / lim, -1, 1) + 1) * 127.5).astype(np.uint8)
    scale = max(1, 512 // max(gray.shape))
    gray = np.kron(gray, np.ones((scale, scale), dtype=np.uint8))
    with open(a.out, "wb") as f:
        f.write(png_bytes(gray))
    print("Wrote %s (%dx%d pixels). Black is a large negative weight, white is a large positive one, gray is near zero." % (a.out, gray.shape[1], gray.shape[0]))


def cmd_graph(a):
    r = load(a.model)
    meta = r.meta
    L = meta["layers"] or 0
    total = sum(int(t.n_elements) for t in r.tensors)
    g = groups(r)
    block0 = [t for t in r.tensors if split_name(t.name)[0] == 0]
    outside = [t for t in r.tensors if split_name(t.name)[0] is None]

    def row(t):
        return "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(split_name(t.name)[1]), "x".join(map(str, shape_of(t))), type_name(t), human(int(t.n_elements)))
    bars = "".join('<div class="bar"><span>%s</span><i style="width:%.1f%%"></i><b>%s (%.1f%%)</b></div>' % (
        k, 100.0 * v / total, human(v), 100.0 * v / total) for k, v in g.items() if v)
    meta_rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (html.escape(k), html.escape(str(v))) for k, v in meta.items() if v is not None)
    doc = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title><style>
:root{--bg:#f6f4ee;--fg:#14213d;--card:#fff;--line:#d9d5c9;--acc:#137a86;--mute:#4a5568}
@media(prefers-color-scheme:dark){:root{--bg:#0f1b2d;--fg:#f2efe6;--card:#1a2b45;--line:#33496b;--acc:#2bb3c0;--mute:#a9b6c8}}
body{margin:0;padding:24px;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,sans-serif}
h1{font-size:28px;margin:0 0 4px}.mute{color:var(--mute)}
.flow{display:flex;flex-direction:column;align-items:stretch;gap:0;max-width:760px;margin:24px 0}
.node{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px}
.node h3{margin:0 0 4px;font-size:18px;color:var(--acc)}
.arrow{text-align:center;color:var(--mute);line-height:1.2}
.block{border:2px dashed var(--acc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:6px}
.inner{display:grid;grid-template-columns:1fr 1fr;gap:8px}@media(max-width:640px){.inner{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%%}td,th{padding:3px 8px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}
.bar{position:relative;height:26px;margin:4px 0;background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden}
.bar i{position:absolute;inset:0 auto 0 0;background:var(--acc);opacity:.35}.bar span,.bar b{position:relative;padding:0 8px;line-height:26px;font-size:14px}.bar b{float:right}
code{font-family:ui-monospace,monospace}
</style></head><body>
<h1>%(title)s</h1><p class="mute">%(fmt)s file. %(total)s parameters. Every box below is a table of numbers. This map is drawn from the file you loaded.</p>
<div class="bar-wrap" style="max-width:760px">%(bars)s</div>
<div class="flow">
<div class="node"><h3>1. Tokens in</h3>Text becomes token ids from a vocabulary of %(vocab)s.</div><div class="arrow">&#8595;</div>
<div class="node"><h3>2. Embedding table</h3>Each token id picks one row: a vector of %(emb)s numbers.</div><div class="arrow">&#8595;</div>
<div class="block"><h3 style="margin:0;color:var(--acc)">3. Transformer block, repeated %(layers)s times</h3>
<div class="node"><b>Normalize</b> (attn_norm / input_layernorm): rescale the vector.</div>
<div class="node"><b>Attention</b>: %(heads)s heads, %(kv)s key/value heads. Q, K, and V matrices turn each token into a question, a label, and a value; scores between tokens decide how the values mix; the O matrix combines the heads.</div>
<div class="node"><b>Add back</b> the input (residual).</div>
<div class="node"><b>Normalize</b> (ffn_norm / post_attention_layernorm).</div>
<div class="node"><b>Feed-forward</b>: gate and up matrices widen the vector to %(ffn)s, a nonlinearity (SiLU) mixes them, the down matrix shrinks it back.</div>
<div class="node"><b>Add back</b> the input (residual).</div>
<details open class="node"><summary><b>Tensors in block 0</b> (all %(layers)s blocks share these shapes)</summary><table><tr><th>name</th><th>shape</th><th>type</th><th>parameters</th></tr>%(b0)s</table></details>
</div><div class="arrow">&#8595;</div>
<div class="node"><h3>4. Final normalize, then the output matrix</h3>One score per vocabulary word. The largest scores become the next-token probabilities.</div>
<details class="node"><summary><b>Tensors outside the blocks</b></summary><table><tr><th>name</th><th>shape</th><th>type</th><th>parameters</th></tr>%(out)s</table></details>
</div>
<details class="node" style="max-width:760px"><summary><b>File settings</b></summary><table>%(meta)s</table></details>
</body></html>""" % dict(title=html.escape(str(meta["name"])), fmt=r.format, total=human(total), bars=bars, vocab=meta["vocabulary"] or "?",
                          emb=meta["embedding size"] or "?", layers=L or "?", heads=meta["attention heads"] or "?",
                          kv=meta["key/value heads"] or "?", ffn=meta["feed-forward size"] or "?",
                          b0="".join(row(t) for t in block0), out="".join(row(t) for t in outside), meta=meta_rows)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("Wrote %s. Open it in your browser." % a.out)


def cmd_compare(a):
    rows = []
    for p in a.models:
        r = load(p)
        total = sum(t.n_elements for t in r.tensors)
        size = sum(t.n_bytes for t in r.tensors)
        types = {}
        for t in r.tensors:
            types[t.dtype] = types.get(t.dtype, 0) + t.n_elements
        main_type = max(types.items(), key=lambda kv: kv[1])[0]
        rows.append((os.path.basename(os.path.normpath(p)), r.format, r.meta.get("architecture"), r.meta.get("layers"),
                     human(total), size_str(size), "%.1f" % (8.0 * size / max(total, 1)), main_type, len(r.tensors)))
    head = ("file", "format", "architecture", "layers", "parameters", "weights", "bits/weight", "main type", "tensors")
    widths = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
    for row in (head,) + tuple(rows):
        print("  ".join(str(x).ljust(w) for x, w in zip(row, widths)))
    print("\nSame idea, different containers: file size is roughly parameters x bits per weight / 8.")


def cmd_scan(a):
    """List the imports a PyTorch pickle would perform, WITHOUT loading it."""
    path = a.model
    blobs = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.endswith(".pkl"):
                    blobs.append((n, z.read(n)))
    else:
        with open(path, "rb") as f:
            blobs.append((os.path.basename(path), f.read()))
    safe = ("torch", "collections.OrderedDict", "numpy", "_codecs.encode", "builtins.set")
    risky = 0
    for name, data in blobs:
        print("Pickle stream: %s" % name)
        found, strings = set(), []
        try:
            for op, arg, _ in pickletools.genops(data):
                if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE"):
                    strings.append(arg)
                if op.name == "GLOBAL":
                    found.add(arg.replace(" ", "."))
                elif op.name == "STACK_GLOBAL" and len(strings) >= 2:
                    found.add(strings[-2] + "." + strings[-1])
        except Exception as e:
            print("  (stopped reading: %s)" % e)
        for g in sorted(found):
            ok = g.startswith(safe)
            risky += not ok
            print("  %-6s %s" % ("ok" if ok else "CHECK", g))
    print("\n%s" % ("Nothing unusual found. Still prefer safetensors." if not risky else
                     "%d import(s) outside torch/numpy. Loading this file could run that code. Do not load it." % risky))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Look inside a model file (GGUF, safetensors, or ONNX)", epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary"); s.add_argument("model"); s.add_argument("--ctx", type=int, default=4096); s.set_defaults(fn=cmd_summary)
    t = sub.add_parser("tensor"); t.add_argument("model"); t.add_argument("name")
    t.add_argument("--count", type=int, default=16); t.add_argument("--corner", type=int, default=8); t.set_defaults(fn=cmd_tensor)
    h = sub.add_parser("heatmap"); h.add_argument("model"); h.add_argument("name")
    h.add_argument("--out", default="heatmap.png"); h.add_argument("--size", type=int, default=128); h.set_defaults(fn=cmd_heatmap)
    g = sub.add_parser("graph"); g.add_argument("model"); g.add_argument("--out", default="model.html"); g.set_defaults(fn=cmd_graph)
    c = sub.add_parser("compare"); c.add_argument("models", nargs="+"); c.set_defaults(fn=cmd_compare)
    k = sub.add_parser("scan"); k.add_argument("model"); k.set_defaults(fn=cmd_scan)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
