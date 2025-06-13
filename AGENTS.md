# AGENTS.md
_Minimal-GPT-2 over fancy-garbling — 7-day sprint_

## 📅  ACTION PLAN
| Day | Milestone | Pass / Fail |
|-----|-----------|-------------|
| 1 | Repo scaffold + toy GC | toy circuit prints |
| 2 | Quantised tensor I/O | MSE <1e-2 |
| 3 | Linear-layer garbling | Δ ≤1 LSB |
| 4 | Activation gadget + FFN | Δ ≤1 LSB |
| 5 | Mini self-attention | attn == ref |
| 6 | 2 blocks + residuals | logits Δ ≤3 LSB |
| 7 | Integration & benchmarks | table in console |

- [ ] Install nightly Rust, fancy-garbling, numpy, torch, transformers
- [ ] Add garbler_cli.rs, evaluator_cli.rs
- [ ] quantize.py + NPZ export
- [ ] matmul circuit (mul_constant + add_constant)
- [ ] LUT ReLU-sign project gate
- [ ] FFN wrap
- [ ] QKV attention + √d scale
- [ ] affine LayerNorm stub
- [ ] driver.py full flow
- [ ] Benchmark numbers
- [ ] *(stretch)* CUDA eval_linear.cu

## 🤖  CUSTOM AGENTS (Cursor / Codex)

### Project Manager
name: PM  
icon: 📋  
shortcut: Cmd+Shift+P  
model: gpt-4o  
enabledTools: [Search, Edit, Terminal]  
instructions: |
  Maintain the checklist above.
  Each morning: report yesterday’s done, today’s plan, blockers.
  Never modify source code directly; assign to engineer agents.

### Rust Engineer
name: Rust Engineer  
icon: 🦀  
shortcut: Cmd+Shift+R  
model: gpt-4o  
enabledTools: [Edit, Run, Terminal]  
instructions: |
  Work only in src/**/*.rs.
  Use Rust 2024 idioms, keep Clippy clean, add unit tests.
  Touch CLI bins last.

### Quant Guru
name: Quant Guru  
icon: 📉  
shortcut: Cmd+Shift+Q  
model: gpt-4o  
enabledTools: [Edit, Run, Terminal]  
instructions: |
  Own model/quantize.py and NPZ export.
  Default modulus q = 251; log per-tensor scales.

### Circuit Architect
name: Circuit Arch  
icon: 🛠️  
shortcut: Cmd+Shift+C  
model: gpt-4o  
enabledTools: [Edit, Terminal]  
instructions: |
  Build circuits with fancy-garbling ArithmeticBMR16.
  Free ops: add, scalar_mul; project gates for non-linears.
  Record gate counts to target/*.csv.

### Benchmark Analyst
name: Bench Analyst  
icon: 📈  
shortcut: Cmd+Shift+B  
model: gpt-4o  
enabledTools: [Run, Terminal, Edit]  
instructions: |
  Automate scripts/driver.py runs.
  Append garbled MB, latency, RSS, label BW to BENCH.md.

### Doc Writer
name: Doc Writer  
icon: 🖋️  
shortcut: Cmd+Shift+D  
model: gpt-4o  
enabledTools: [Edit]  
instructions: |
  Keep README and rustdoc up-to-date.
  Document fancy-garbling limits vs. rate-1 AG.

## 🗂  Repo tree
.
├── AGENTS.md
├── Cargo.toml
├── src/
│   ├── bin/garbler_cli.rs
│   ├── bin/evaluator_cli.rs
│   └── lib.rs
├── model/gpt2_2blk_quant.npz
├── model/quantize.py
└── scripts/driver.py
