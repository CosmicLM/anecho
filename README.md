# Anecho
> *Silencing the noise in the NISQ era.*

**Anecho** is a hardware-agnostic error mitigation library and engine designed to bridge the gap between noisy quantum hardware and reliable algorithmic results. 

Currently in active development, Anecho focuses on **Zero-Noise Extrapolation (ZNE)** techniques that are adaptable to both Superconducting (IBM) and Neutral Atom (PASQAL) architectures.

## Key Features (Roadmap)
- [ ] **Hardware Agnostic:** compatible with Qiskit, Pulser (WIP), and Qadence.
- [ ] **Modular Extrapolation:** Plug-and-play support for Linear, Polynomial, and Exponential folding.
- [ ] **Calibration Aware:** Adjusts mitigation strategies based on daily backend T1/T2 properties.
