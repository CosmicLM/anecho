# Build Roadmap — Aug to Dec 2026

Week-by-week plan from **2026-08-10** to the capstone deadline of
**2026-12-31**. Deliverables are a written paper and a working repo.

## How this plan is ordered

It is **not** one component per week. Two principles override that:

1. **End-to-end before deep.** A stubbed version of the entire pipeline exists
   and runs by W3. Every week after that improves a number that is already
   being measured, so there is never a state of "lots of code, no results."
2. **Risk first.** The thesis claim gets tested in **W7 of 18**, not at the end.
   If it fails, seven weeks of runway remain to pivot the claim — which is a
   recoverable problem in W7 and a fatal one in W15.

The thesis being tested:

> Layer-resolved noise profiling can select ZNE scale factors and extrapolation
> model per circuit, beating fixed-parameter ZNE at equal shot budget.

## Budget reality

| | |
| --- | --- |
| Calendar weeks | 21 (Aug 10 – Dec 31; W21 is partial) |
| Working weeks planned | 18 (W1–W18) |
| Realistic working pace | 8–10 h/week alongside coursework |
| Total | ~130–160 h |
| Thanksgiving | Nov 26 (W16) |
| Finals | ~W17–W18 — assume near-zero throughput |
| **Internal ship date** | **W18, Dec 13** |
| Deadline | Dec 31 (W21) |

W19–W21 are slack, not workspace. If the plan is consuming them, something
earlier has to be cut — see [What to cut](#what-to-cut-when-behind).

!!! tip "The weekly ritual"
    End every week by appending to `docs/lab-notebook.md`: what you ran, the
    number you got, what you expected, what surprised you. Eighteen of those
    entries *are* the paper's methods and results sections. This is the single
    highest-leverage habit in the plan — it turns thesis writing from a
    December wall into an additive task.

---

## Phase 1 — Foundation and walking skeleton (W1–W3)

### W1 · Aug 10–16 · Repo foundation
**~8 h**

- `pyproject.toml` with src layout; `pip install -e .` works
- `pytest` configured; one real test passing
- `ruff` for linting; GitHub Actions running lint + tests on push
- Consolidate environments: delete the duplicate `experiments/venv/`, pin
  dependencies
- Create `docs/lab-notebook.md`

**Done when:** a clean clone runs `pip install -e . && pytest` green, and CI
passes on a pushed commit.

### W2 · Aug 17–23 · Observables and shot-based estimation
**~9 h**

This is the foundation the entire thesis rests on — get the shot accounting
right here and everything downstream is measurable.

- `anecho/observables.py` — Pauli-string observables; parity `⟨Z⊗Z⊗…⟩` for GHZ;
  Hamiltonian expectation for the hardware-efficient ansatz
- `anecho/execute.py` — run a circuit at `N` shots, return `⟨O⟩` **and its
  standard error**, with shots consumed recorded explicitly

**Done when:** `⟨O⟩ ± σ` is produced for any (circuit, observable, backend,
shots), and a test confirms `σ` shrinks as `1/√N`.

!!! warning "Do not use `method='density_matrix'` here"
    Exact `ρ` has no sampling error and will hide ZNE's entire cost. See
    [Noise Models](references/noise.md). Density matrix stays available as
    ground truth for *bias* measurement only.

### W3 · Aug 24–30 · Walking skeleton — end-to-end ZNE
**~9 h**

- `anecho/folding.py` — global folding, `λ ∈ {1, 3, 5}`
- `anecho/extrapolate.py` — linear and Richardson
- `anecho/pipeline.py` — `run()` tying it together

**Done when:** `anecho.run(ghz(4), parity, backend, shots=8192)` returns an
extrapolated value end to end. **The number will be mediocre. Ship it anyway** —
that is the point of a skeleton. First results row in the lab notebook.

---

## Phase 2 — Making the measurement trustworthy (W4–W5)

### W4 · Aug 31–Sep 6 · Equal-budget benchmark harness
**~9 h** · *Fall term likely starts around here — protect the time.*

The methodological centerpiece. Comparing unmitigated-at-`N` against
ZNE-at-`N`-per-scale-factor silently hands ZNE 3× the budget; that comparison is
worthless and a committee will find it.

- Harness running every arm at **matched total shots**: unmitigated at `S`
  vs ZNE at `S/3` per `λ`
- Repeat over ~20 seeds; report mean and spread of `|⟨O⟩_est − ⟨O⟩_ideal|`
- Emit a tidy CSV — this replaces `quantum_benchmarks.csv` and its placeholders

**Done when:** a real table exists comparing arms at equal budget.

!!! danger "ZNE may lose this comparison"
    At equal budget and low noise, ZNE's variance cost can exceed its bias
    benefit. That is a legitimate, publishable finding — report it honestly
    rather than tuning the budget until ZNE wins.

### W5 · Sep 7–13 · Validate against Mitiq
**~8 h**

Without an external check, "my ZNE implementation" is an unverified claim.

- Install Mitiq; run identical circuits through both
- Reconcile any disagreement — a discrepancy is a bug in yours until proven
  otherwise

**Done when:** Anecho and Mitiq agree within error bars on the same inputs, with
any deliberate differences documented. This is the correctness argument for the
whole paper.

---

## Phase 3 — The thesis (W6–W8)

### W6 · Sep 14–20 · Layer profiler
**~10 h**

Regime A from [Layer Profiling](references/layer-profiling.md) — matches your
qubit scale and reuses `Statevector`/`state_fidelity`.

- `anecho/profile.py` — prefix-circuit truncation, per-layer fidelity
- Decay trajectory for GHZ / QFT / hardware-efficient at 4, 6, 8, 10 qubits

**Done when:** decay curves are plotted and committed for all three families.

### W7 · Sep 21–27 · ⚠ THE EXPERIMENT
**~10 h** · **The highest-risk week in the plan.**

- Selection rule: map profile features (decay rate, curvature, depth) to
  `(λ set, extrapolator)` — e.g. exponential-looking decay selects the
  exponential extrapolator; decay rate sets `λ` spacing
- Run adaptive vs fixed-parameter baseline at equal budget

**Done when:** you know whether the thesis holds — in W7 of 18, with half the
runway left to respond.

### W8 · Sep 28–Oct 4 · Buffer and decision point
**~9 h** · *Deliberately unallocated.*

Branch on W7:

- **Thesis held** → strengthen it: more circuits, more qubit counts, significance testing
- **Thesis failed** → diagnose and pivot the claim. "The profile predicts *when*
  ZNE helps and when it costs more than it returns" is weaker, true, and still a
  complete thesis
- **W7 overran** → finish it here

**Done when:** the thesis claim is written down in the lab notebook in the exact
form the W7 data supports — either the original wording, or a narrowed one. The
rest of the plan is built on whatever you write here, so do not leave it
ambiguous.

---

## Phase 4 — Hardening the result (W9–W10)

### W9 · Oct 5–11 · Blind validation on FakeKyoto
**~9 h**

Profiling a noise model you wrote yourself is circular. `FakeKyoto` carries real
calibration snapshots the profiler must discover.

- Swap the synthetic depolarizing model for `FakeKyoto`
- **Handle qubit routing.** Heavy-hex connectivity forces routing, so transpiled
  qubit order will not match logical order. Fidelity across that mismatch is
  silently wrong, not visibly broken — permute back via the final layout. See
  [Noise Models](references/noise.md#known-trap-routing-permutes-qubits)

**Done when:** the W7 result either reproduces under realistic noise or is shown
not to — both are reportable.

### W10 · Oct 12–18 · Statistics and the headline table
**~9 h**

- Bootstrap confidence intervals; paired tests across seeds
- Full sweep: 3 circuit families × 4 qubit counts × 2 backends × {unmitigated,
  fixed ZNE, adaptive ZNE}

**Done when:** the paper's headline table regenerates from a single command,
with error bars.

!!! success "The thesis is defensible from here"
    Everything after this point is additive. If the semester goes sideways in
    November, you still have a complete result.

---

## Phase 5 — Additive work (W11–W13)

*All three weeks are droppable. None is on the thesis critical path.*

### W11 · Oct 19–25 · SPAM mitigation
**~9 h**

Matrix-free and M3-style, per your *SPAM Characterization* design note. Do
**not** build the dense `2ⁿ × 2ⁿ` inversion — it stops being tractable in the
double-digit qubit range. The method to follow is Nation, Kang, Sundaresan,
Gambetta, *Scalable mitigation of measurement errors on quantum computers*
(2021, PRX Quantum) —
<https://link.aps.org/pdf/10.1103/PRXQuantum.2.040326>

**Done when:** SPAM is an optional pipeline stage with its incremental effect
measured on top of adaptive ZNE.

### W12 · Oct 26–Nov 1 · Real hardware run
**~8 h**

You have no IBM Quantum account yet (`~/.qiskit` does not exist), so budget
setup friction plus queue time.

- Create the account, verify the current open-plan runtime allowance before
  spending any of it
- Spend it on **one** confirmation run: smallest circuit that makes the point

**Done when:** one real-hardware data point corroborates the simulated result.
Even 4-qubit GHZ is enough — this is a corroboration, not a study.

### W13 · Nov 2–8 · One Rust kernel
**~10 h**

- Profile the Python pipeline first; find the actual hot path
- Port exactly one function via PyO3/maturin; measure before and after

**Done when:** a speedup curve exists. If profiling shows no bottleneck worth
porting, **write that down and skip the port** — "I profiled it and Rust was not
warranted at this scale" is a stronger engineering result than an unjustified
rewrite, and it buys back a week.

---

## Phase 6 — Delivery (W14–W18)


### W14 · Nov 9–15 · Docs and API polish
**~9 h**

`mkdocstrings` finally has real code to document. Rewrite the README against
what actually shipped; add a one-command script that reproduces every figure.

**Done when:** `mkdocs build --strict` passes with real API reference, and a
stranger can reproduce the results table from the README.

### W15 · Nov 16–22 · Paper — methods and results
**~10 h**

The heaviest writing week, scheduled before Thanksgiving and finals rather than
after. Both sections are largely assembly if the lab notebook has been kept.

- Methods: the pipeline, the equal-budget protocol, the Mitiq validation
- Results: W10's headline table, plus the decay curves from W6

**Done when:** methods and results are drafted end to end, and every number in
them traces back to a dated lab-notebook entry.

### W16 · Nov 23–29 · Thanksgiving week — low-demand sections
**~4 h** · Thanksgiving is Nov 26.

Deliberately the lightest week in the plan. Introduction, background, and
related work are the most interruptible sections — they need reading and
citation, not sustained reasoning, so they survive being done in fragments.

- Introduction and problem statement
- Related work: Mitiq, M3, layer fidelity, the folding literature already
  collected in [Layer Profiling](references/layer-profiling.md)

**Done when:** introduction and related work are drafted with citations pulled.

### W17 · Nov 30–Dec 6 · Discussion and limitations
**~6 h** · Finals begin to dominate.

State the limitations plainly. Each is already documented, and pre-empting them
reads as rigor; being asked about them cold does not.

- ZNE's variance cost, and how the equal-budget protocol accounts for it
- State fidelity being simulation-only — why the headline observable is
  QPU-measurable instead
- Regime A profiling not generalizing past ~25–30 qubits
- Exactly what W12's single hardware point can and cannot support
- Anything the W7 result failed to show

**Done when:** discussion and limitations are drafted.

### W18 · Dec 7–13 · Full-draft revision — **the real ship date**
**~6 h**

Read the whole thing start to finish in one sitting and fix the seams between
sections written weeks apart. Write the abstract and conclusion **last**, once
you know what the paper actually says.

**Done when:** a complete draft exists that you would submit if forced to today.

!!! danger "Treat Dec 13 as the deadline, not Dec 31"
    Everything after this week is buffer that finals will probably consume. A
    plan that requires W19–W21 to go well is a plan with no margin at all.

---

## Phase 7 — Buffer and submission (W19–W21)

*These three weeks exist to absorb overrun. The checklists below are what to do
only if nothing needs absorbing — they are not scheduled work.*

### W19 · Dec 14–20 · Absorption, or reproducibility audit
**~4 h**

If W1–W18 landed clean, spend this catching the failure that embarrasses
capstones: results that only reproduce on the machine that made them.

- Clone the repo fresh into a clean venv, install from the pinned deps
- Regenerate every figure and the headline table from scratch
- Fix whatever breaks — hardcoded paths, unpinned versions, unseeded RNG

**Done when:** a fresh clone reproduces the headline table without manual
intervention.

### W20 · Dec 21–27 · Absorption, or final polish
**~3 h**

- Proofread the full draft
- Freeze dependency versions; tag a release
- Confirm `mkdocs build --strict` still passes against the final code

**Done when:** the repo is tagged and the draft is proofread.

### W21 · Dec 28–31 · Submission
**~2 h** · Partial week — the deadline lands Dec 31.

Submit. **Build nothing new this week.** Any change made here is a change
nobody has time to verify.

**Done when:** submitted.

---

## What to cut when behind

In order, cut first to last:

1. **W13 Rust kernel** — pure engineering flourish; the thesis is untouched
2. **W12 hardware run** — nice corroboration, but the simulated result stands
3. **W11 SPAM** — a second technique, not the claim
4. **W9 FakeKyoto** — weakens generality, but W7+W10 still constitute a result

**Never cut:** W2 (shot accounting), W4 (equal budget), W5 (Mitiq validation),
W7 (the experiment), W10 (statistics). Those five are the thesis. Everything
else is supporting material.

## Already out of scope

Dropped from the original architecture roadmap to fit the timeline; carry them
as future work in the paper:

- CUDA acceleration layer (`cudarc`, cuBLAS, cuSOLVER)
- `cuQuantum` / `cuTensorNet` tensor-network contraction
- The post-ZNE Ising solver and CUDA parallel tempering
- Adaptive mid-circuit recompilation against live hardware
- Multi-backend support beyond Qiskit (Pulser, Qadence)
