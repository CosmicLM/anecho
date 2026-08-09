# Noise Models

!!! note "Status: prototype"
    The models below are what the scripts in `experiments/` currently use.
    There is no configurable noise-model layer in `src/anecho/` yet.

Anecho works against two kinds of noise source, used for different purposes.

## 1. Synthetic depolarizing model

Used by `experiments/benchmarks.py` for scaling studies. A hand-written model
keeps the simulation small — building a full 127-qubit backend model to run a
10-qubit circuit wastes memory for no benefit.

```python
noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 2), ['cx'])
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.005, 1), ['h', 'rx', 'ry'])
```

| Parameter | Value | Applies to |
| --- | --- | --- |
| Two-qubit depolarizing rate | `0.02` | `cx` |
| Single-qubit depolarizing rate | `0.005` | `h`, `rx`, `ry` |

This model is **uniform and memoryless**: every qubit has identical error rates,
and there is no `T1`/`T2` decoherence, no readout error, and no crosstalk.
That makes it a clean testbed for extrapolation behaviour, but it will
*understate* how hard real mitigation is — in particular, folding amplifies
decoherence and depolarizing noise at different rates, and this model has no
decoherence to amplify. See [ZNE Manager](zne.md).

## 2. Hardware-derived fake backends

Used by `experiments/01_baseline_noise.py`. Qiskit's fake providers carry
snapshots of real calibration data — per-qubit `T1`/`T2`, gate errors, readout
error, and the physical coupling map.

```python
from qiskit_ibm_runtime.fake_provider import FakeKyoto
noisy_backend = AerSimulator.from_backend(FakeKyoto())
```

This is the right noise source for validating the layer profiler: the profiler
can treat the backend's noise as *unknown* and be scored on how well it
recovers it. Profiling a hand-written model, by contrast, is circular — it only
measures the parameters that were typed in above.

## Simulation methods

| Method | Sampling error | Use |
| --- | --- | --- |
| `density_matrix` | none — exact `ρ` | Ground-truth bias measurement |
| `automatic` / shot-based | yes | Anything evaluating a mitigation technique |

!!! danger "Exact `ρ` cannot evaluate mitigation"
    `experiments/benchmarks.py` runs with `method='density_matrix'`, which
    returns the exact density matrix with zero shot noise. Since ZNE trades bias
    for variance, a zero-variance harness makes it look free. Mitigation
    benchmarks need finite shots.

## Known trap: routing permutes qubits

Comparing a noisy state against `Statevector.from_instruction(circuit)` is only
valid while `transpile` leaves qubit order untouched. That currently holds in
`benchmarks.py` because `AerSimulator` with a bare noise model has **no coupling
map**, so the layout stays trivial.

It stops holding the moment a backend with real connectivity is used —
`FakeKyoto`'s heavy-hex lattice forces routing, and the transpiled circuit's
physical qubit order will not match the logical one. Fidelity computed across
that mismatch is silently wrong, not obviously broken. Use the transpiled
circuit's final layout to permute back before comparing.

## References

- Georgopoulos, Emary, Zuliani — *Modelling and Simulating the Noisy Behaviour
  of Near-term Quantum Computers* (2021, Phys. Rev. A 104, 062432) —
  <https://arxiv.org/abs/2101.02109>
- McKay, Hincks, Pritchett et al. — *Benchmarking quantum processor performance
  at scale* (2023) — layer fidelity on real backends —
  <https://arxiv.org/pdf/2311.05933>
