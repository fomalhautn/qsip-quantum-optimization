# QSIP Quantum Optimization

Educational materials for the QSIP Quantum Hackathon (5–6 November 2026).

**[Hackathon event](https://enccs.se/event/qsip-hackathon-quantum-cryptography-qml/)** · Website hosted using GitHub Pages

## The challenges

**Max-Cut (beginner)** — Divide a six-node graph into two groups to maximize the number of edges crossing between them. Follow the problem from binary variables and QUBO to an Ising cost operator, QAOA simulation and classical benchmarking.

**Brain-network communities (advanced)** — Find groups of strongly interconnected nodes in a synthetic weighted graph by maximizing network modularity. Compare a classical optimum with QAOA simulations and optional IQM hardware measurements.

## How the experiments work

The notebooks use a simulator to optimize the adjustable QAOA circuit angles ($\gamma$, $\beta$). The optional IQM hardware stage runs the **same already-optimized circuit** to compare real measurements; it does **not** repeatedly optimize circuit parameters on the quantum processor. Repeated hardware-training experiments are an optional extension: [IQM Training the QAOA](https://docs.iqm.tech/4.6/iqm-qaoa/Training%20the%20QAOA.html).

## What the project contains

- `index.html` — interactive introduction and challenge links
- `notebooks/` — two guided Jupyter exercises and a brief starting notebook
- `qsip_quantum.py` — reproducible graph and QAOA helpers
- `downloads/` — notebooks and dependencies for optional local execution

Public Binder is for **simulation only**. IQM hardware use is optional, requires authorized access, and should be done locally or in a trusted Jupyter environment. API tokens must not be entered into public Binder or committed to GitHub.

## Scientific basis

- Farhi, Goldstone & Gutmann (2014), [A Quantum Approximate Optimization Algorithm](https://arxiv.org/abs/1411.4028)
- Newman (2006), [Modularity and community structure in networks](https://doi.org/10.1073/pnas.0601602103)
- [IQM Qiskit user guide](https://docs.iqm.tech/iqm-client/user_guide_qiskit.html)

All datasets are **synthetic**. The notebooks are independent educational implementations, not reproductions of IQM case studies or demonstrations of quantum advantage.
