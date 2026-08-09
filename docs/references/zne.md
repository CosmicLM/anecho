# ZNE Manager

!!! note "Status: not implemented"
    This page documents the intended design. `src/anecho/` contains no ZNE code
    yet. The `ZNE_Linear` / `ZNE_Poly` columns in
    `experiments/quantum_benchmarks.csv` are placeholder arithmetic, not output
    from anything described here.

Zero-Noise Extrapolation estimates an observable's noise-free expectation value
without ever running a noise-free circuit. It runs the circuit at several
*amplified* noise levels, then extrapolates the resulting curve back to zero.

ZNE mitigates **expectation values of observables**, not quantum states. The
output of a ZNE run is a scalar `⟨O⟩`, not a corrected density matrix.

## Step 1 — Noise scaling by unitary folding

For a circuit implementing unitary `U`, folding replaces it with

```
U  →  U (U† U)^k
```

which is logically identical to `U` for any integer `k ≥ 0` (each `U† U` is the
identity), but runs `2k + 1` times as many gates. The noise scale factor is

```
λ = 2k + 1        →   λ ∈ {1, 3, 5, 7, ...}
```

| Symbol | Meaning |
| --- | --- |
| `U` | the target circuit's unitary |
| `U†` | its conjugate transpose (the inverse circuit) |
| `k` | number of folds applied |
| `λ` | resulting noise scale factor |

**Global folding** applies this to the whole circuit. **Local folding** applies
it to individual gates, which reaches non-integer `λ` at finer granularity.
Both come from Giurgica-Tiron et al., *Digital zero noise extrapolation for
quantum error mitigation* (2020) — <https://arxiv.org/pdf/2005.10921v2>.

!!! warning "Folding is not noise-type neutral"
    Folding triples gate count per fold level, so it amplifies **decoherence**
    (T1/T2, wall-clock dependent) faster than **depolarizing** gate noise. The
    two do not scale together with `λ`. A ZNE result on a decoherence-dominated
    backend is not directly comparable to one on a gate-error-dominated backend.

## Step 2 — Extrapolation to λ = 0

Given measurements `⟨O⟩_λ` at scale factors `λ₁ … λₙ`, fit a model and evaluate
it at `λ = 0`. Planned models:

- **Linear** — two or more points, minimal variance cost, biased when the true
  curve bends.
- **Polynomial / Richardson** — exact for a degree-`n−1` noise expansion.
- **Exponential** — matches the physically-motivated decay `⟨O⟩_λ = a + b·e^(−cλ)`.

## The variance cost

Richardson extrapolation is a *linear* combination of the measured points:

```
⟨O⟩_0  =  Σᵢ γᵢ ⟨O⟩_λᵢ          with   Σᵢ γᵢ = 1
```

The coefficients sum to one, but they alternate in sign and exceed one in
magnitude, so the estimator's variance inflates by `Σᵢ γᵢ²`:

| Scale factors | Coefficients `γ` | Variance | Std. error |
| --- | --- | --- | --- |
| `{1, 2, 3}` | `+3, −3, +1` | `19.0×` | `4.36×` |
| `{1, 3, 5}` | `+1.875, −1.25, +0.375` | `5.22×` | `2.28×` |
| `{1, 3, 5, 7}` | `+2.1875, −2.1875, +1.3125, −0.3125` | `11.39×` | `3.38×` |

ZNE trades **bias** for **variance**. With `λ = {1, 3, 5}`, matching the error
bars of an unmitigated run costs roughly `3 × 5.22 ≈ 15.7×` the total shots —
3× for the extra circuit executions, 5.22× for the variance inflation.

!!! danger "Benchmarks must hold the shot budget constant"
    Comparing unmitigated-at-`N`-shots against ZNE-at-`N`-shots-per-scale-factor
    silently hands ZNE 3× the budget. A fair comparison gives both arms the same
    *total* shots. An exact-`ρ` simulation (`method='density_matrix'`) has no
    sampling error at all, so it cannot surface this cost — ZNE will appear free.

## Planned API

```python
from anecho.zne import ZNEManager

mgr = ZNEManager(scale_factors=[1, 3, 5], extrapolator="richardson")
result = mgr.run(circuit, observable, backend, shots=8192)

result.value          # extrapolated ⟨O⟩ at λ = 0
result.raw            # {λ: ⟨O⟩_λ} measured at each scale factor
result.std_error      # propagated, including the Σγ² inflation
```

## References

- Giurgica-Tiron, Hindy, LaRose, Mari, Zeng — *Digital zero noise extrapolation
  for quantum error mitigation* (2020) — <https://arxiv.org/pdf/2005.10921v2>
- Wahl, Mari, Shammah et al. — *Zero noise extrapolation on logical qubits by
  scaling the error correction code distance* (2023) —
  <https://arxiv.org/pdf/2304.14985>
- Endo, Benjamin, Li — *Practical Quantum Error Mitigation for Near-Future
  Applications* (2018) — the quasi-probability alternative to folding —
  <http://link.aps.org/pdf/10.1103/PhysRevX.8.031027>
