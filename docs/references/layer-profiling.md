# Layer / Micro-Shot Noise Profiling — Literature & Design Notes

Grounding notes for the pipeline's Step 2 (Dynamic Micro-Shot Profiling), plus
the SPAM, ZNE, twirling, and Ising-solver steps it feeds into. Every paper
below was pulled from a live academic search (arXiv/Crossref/Semantic
Scholar/OpenAlex), not recalled from memory — links are real and were checked
to resolve.

## "Micro-shot slicing" doesn't exist as a named technique — here's what it maps to

No paper uses that phrase. The idea (truncate a circuit layer-by-layer,
measure each prefix, watch fidelity decay with depth) is real and well
established, but it splits into two regimes depending on circuit size, and
conflating them will silently break past a certain qubit count:

**Regime A — small enough to classically verify (roughly ≤ 25–30 qubits,
statevector-simulable).** This is where Anecho's current experiments already
live (`benchmarks.py` goes up to 10 qubits). Here, literal truncation works
exactly as the pipeline describes: build N prefix circuits, get each prefix's
*exact* ideal output via `Statevector.from_instruction()` (cheap — no shots
needed for the ideal side, `benchmarks.py` already does this), run only the
*noisy* prefix on hardware/Aer with a small shot count, and compute
`state_fidelity(ideal, noisy)` per layer.

**Regime B — real/larger hardware, where you can't classically simulate the
ideal state.** This is what IBM's **Layer Fidelity (LF) / Error Per Layered
Gate (EPLG)** benchmark solves:

> McKay, Hincks, Pritchett et al., *"Benchmarking quantum processor
> performance at scale"* (2023) — https://arxiv.org/pdf/2311.05933

Instead of truncating *your* circuit, LF interleaves **random 2-qubit
Clifford layers** matching your circuit's connectivity pattern. Random
Cliffords are the trick: their ideal output IS efficiently computable
(stabilizer simulation, not statevector), so you get a verifiable fidelity
number per layer at *any* qubit count, not just classically-simulable ones. A
2025/2026 follow-up tunes the method further:

> Lozano Palacio, Nayfeh, Ware et al., *"Parameter Analysis and Optimization
> of Layer Fidelity for Quantum Processor Benchmarking at Scale"* (2025) —
> https://arxiv.org/pdf/2510.16915

And a related refinement jointly characterizes multiple layers at once for
better accuracy than single-layer estimates:

> Calzona, Papič, Figueroa-Romero et al., *"Multilayer cycle benchmarking for
> high-accuracy error characterization"* (2026, Phys. Rev. Research) —
> https://link.aps.org/pdf/10.1103/4hbl-hpl3

**Design implication:** build Regime A first (it matches your current
experiment scale exactly and reuses `state_fidelity`/`Statevector` you
already import in `benchmarks.py`), but don't assume it generalizes — past
~25-30 qubits you'd need to switch the "ideal reference" from statevector
simulation to Clifford-layer substitution per McKay et al., not just throw
more compute at the same approach.

## How many shots is "micro"? — don't just guess a small number

The pipeline says "small shot count" for the diagnostic probe. There's a
principled way to pick it instead of a flat guess:

> Kim, Jang, Kim et al., *"Distribution-adaptive dynamic shot optimization
> for variational quantum algorithms"* (2025, Phys. Rev. Research; also
> arXiv:2412.17485) — https://arxiv.org/pdf/2412.17485.pdf

Core idea: allocate shots per-layer based on the *observed estimator
variance* so far, not a fixed number — layers whose output distribution is
already stable get fewer shots, noisy/uncertain layers get more, within a
total shot budget. This is directly reusable for Step 2: instead of "N shots
per prefix circuit," track running variance across prefixes and shift the
budget toward the layers where the fidelity trajectory is actually
ambiguous.

## SPAM — a real scaling caveat for the "invert the calibration matrix" plan

> Nation, Kang, Sundaresan, Gambetta, *"Scalable mitigation of measurement
> errors on quantum computers"* (2021, PRX Quantum) — this is the **M3**
> method IBM ships in Qiskit — https://link.aps.org/pdf/10.1103/PRXQuantum.2.040326

M3's whole reason for existing: a naive assignment-probability matrix is
`4^n × 4^n` (2^n if you only track diagonal bias) — a direct cuBLAS
inversion, as Step 1 currently plans, becomes intractable well before you'd
expect (double-digit qubit counts, not hundreds). M3 avoids ever forming the
full matrix — it solves the correction **matrix-free**, iteratively,
scoped only to the bitstrings actually observed. If Anecho's SPAM step is
meant to scale past toy circuit sizes, the matrix-free approach is the one
to actually implement, with dense cuBLAS inversion reserved for genuinely
small qubit counts where it's still cheap.

## ZNE via unitary folding — source of the exact formula, plus a real limitation

> Giurgica-Tiron, Hindy, LaRose, Mari, Zeng, *"Digital zero noise
> extrapolation for quantum error mitigation"* (2020, QCE) —
> https://arxiv.org/pdf/2005.10921v2

This is the paper the pipeline's `U → U·U†·U` folding formula comes from —
worth reading directly since it also covers *local* folding (fold individual
gates, not the whole circuit) as a finer-grained noise-scaling alternative to
global folding.

Real caveat worth designing around: folding **triples gate count** per fold
level, which amplifies *decoherence* (T1/T2, time-dependent) noise
disproportionately compared to *gate* (depolarizing) noise — the two don't
scale the same way with added idle/gate time. A related paper applying ZNE at
the logical-qubit level discusses exactly this noise-type sensitivity:

> Wahl, Mari, Shammah et al., *"Zero noise extrapolation on logical qubits by
> scaling the error correction code distance"* (2023) —
> https://arxiv.org/pdf/2304.14985

The foundational alternative (quasi-probability, not folding) is worth
knowing about even if not implemented first:

> Endo, Benjamin, Li, *"Practical Quantum Error Mitigation for Near-Future
> Applications"* (2018, PRX) — http://link.aps.org/pdf/10.1103/PhysRevX.8.031027

## Pauli twirling — real basis for the "inject error-canceling Pauli twirling" step

> Hashim, Naik, Morvan et al., *"Randomized compiling for scalable quantum
> computing on a noisy superconducting quantum processor"* (2020/2021, PRX) —
> https://arxiv.org/pdf/2010.00215

This is the real technique: twirling converts *coherent* errors (which
compound unpredictably and don't average out) into stochastic Pauli errors
(which do average out, and which ZNE/M3 are actually designed to handle). If
Anecho's circuits are Clifford-heavy this applies directly; if they're
variational (arbitrary rotation angles — non-Clifford), the twirling group
itself needs adjusting:

> Santos, Bar, Uzdin, *"Pseudo twirling mitigation of coherent errors in
> non-Clifford gates"* (2024, npj Quantum Information) —
> https://arxiv.org/pdf/2401.09040.pdf

## Post-ZNE Ising solver — standard comparison to design against

> Wang, Machta, Katzgraber, *"Comparing Monte Carlo methods for finding
> ground states of Ising spin glasses: Population annealing, simulated
> annealing, and parallel tempering"* (2015, Phys. Rev. E) —
> https://arxiv.org/pdf/1412.2104v2

This is the standard head-to-head of exactly the three methods the pipeline
mentions (SA, PT, and population annealing as a hybrid of both) — worth
reading before committing to PT specifically, since population annealing is
described here as combining PT's ability to cross energy barriers with SA's
simplicity, and may parallelize onto GPU differently (population-level
parallelism vs. replica-level).

## A concrete finding from reviewing the current code

`experiments/benchmarks.py`'s `ZNE_Linear`/`ZNE_Poly` columns are **not**
computed from a real ZNE run — they're a fixed fudge factor:

```python
writer.writerow([c_type, q_count, "ZNE_Linear", min(1.0, round(fid + 0.10, 4))])
writer.writerow([c_type, q_count, "ZNE_Poly", min(1.0, round(fid + 0.15, 4))])
```

Fine as a placeholder while the pivot-table shape is being worked out, but
worth flagging clearly so it's never mistaken for real mitigation data —
right now `quantum_benchmarks.csv` doesn't demonstrate ZNE actually working,
it demonstrates the *reporting format* for when it does.

## Suggested concrete next step

Write `src/anecho/layer_profile.py` implementing the Regime A profiler above
(prefix-circuit truncation + `Statevector`/`state_fidelity`, matching your
current qubit-count scale and reusing what `benchmarks.py` already imports),
then wire its real per-layer fidelity trajectory into `benchmarks.py` in
place of the `fid + 0.10` placeholder. Layer Fidelity (Regime B) is the
natural follow-up once real hardware or larger circuits are in scope.
