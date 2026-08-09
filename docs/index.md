# Anecho

> *Silencing the noise in the NISQ era.*

Anecho is a hardware-agnostic error mitigation library targeting the gap between
noisy quantum hardware and reliable algorithmic results. It focuses on
**Zero-Noise Extrapolation (ZNE)** driven by a layer-resolved noise profile,
rather than ZNE with fixed, hand-chosen parameters.

## Current status

Anecho is in the **research and prototype** phase. `src/anecho/` does not yet
contain library code — the work so far lives in `experiments/` and in the design
notes under [References](references/layer-profiling.md).

| Component | State |
| --- | --- |
| Baseline noise characterization | Prototype — `experiments/01_baseline_noise.py` |
| Circuit benchmark harness | Prototype — `experiments/benchmarks.py` |
| ZNE engine | Not implemented — see [ZNE Manager](references/zne.md) |
| Noise models | Prototype — see [Noise Models](references/noise.md) |
| Layer / micro-shot profiler | Design complete — see [Layer Profiling](references/layer-profiling.md) |
| SPAM mitigation | Design only |

!!! warning "The benchmark CSV does not yet demonstrate mitigation"
    The `ZNE_Linear` and `ZNE_Poly` rows in `experiments/quantum_benchmarks.csv`
    are placeholders (`fidelity + 0.10` and `fidelity + 0.15`), not the output of
    a real ZNE run. The file currently demonstrates the *reporting format*, not
    working mitigation.

## The three-step pipeline

1. **Pre-circuit SPAM mitigation** — build a classical assignment probability
   matrix from calibration circuits and correct the measured distribution
   against it, before the target circuit runs.
2. **Dynamic micro-shot profiling** — truncate the target circuit layer by
   layer, measure each prefix, and track the fidelity decay trajectory to build
   a noise profile of the backend.
3. **Zero-noise extrapolation** — scale noise upward by unitary folding, record
   the observable at each amplified level, and extrapolate back to zero.

The step 2 → step 3 coupling is the part specific to Anecho: the profile from
step 2 selects the scale factors and extrapolation model used in step 3. ZNE on
its own is available in Mitiq, and SPAM correction on its own ships in Qiskit as
M3.

## Repository layout

```
src/anecho/      library code (empty — pending)
experiments/     prototype scripts and benchmark output
tests/           test suite (empty — pending)
notebooks/       exploratory notebooks
docs/            this documentation
```

## Building the docs

```bash
./venv/bin/mkdocs serve     # live preview at http://127.0.0.1:8000
./venv/bin/mkdocs build     # render to site/
```
