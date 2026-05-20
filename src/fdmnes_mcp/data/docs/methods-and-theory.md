---
date: 2026-05-19
project: fdmnes
type: docs-theory
---

# FDMNES — methods, theory, defaults, scope

Companion to the [docs index](2026-05-19-docs-overview.md). Distilled from the English manual (Joly, 2026-03-10), the upstream `FDMNES_Modifications.txt` change log, and direct reading of the source.

## 1. Scope of the code

FDMNES computes:

| Spectroscopy | Mode keyword(s) | Output file(s) |
|---|---|---|
| XANES | (default) | `X.txt`, `X_conv.txt` |
| EXAFS-range | `FDMX`, `FDMX_proc` | same prefix, FDMX-style absorption schedule |
| XMCD / circular dichroism | `Magnetism` + `Polarize` circular | columns split sum / difference |
| RXS / DAFS / anomalous diffraction | `DAFS` (alias `RXS`) | `X_scan.txt`, `X_scan_conv.txt` |
| RIXS 2D maps | `RIXS` (+ `Energ_rixs`) | RIXS energy maps |
| NRIXS / X-Raman | `NRIXS`, `NRIXS_mono`, `All_nrixs` | `X_nrixs.txt` (replaces `X.txt`) |
| Optical / dielectric / CD | `Optic` (often + `TDDFT`) | optical spectra |
| Emission (XES) | `XES`, `Photoemission` | emission spectra |
| Surface resonant XRD (SRXRD) | `DAFS_2D`, `Film` + `Bulk` + ... | 2D-RXD intensities |

Some are mutually exclusive (`Crystal` vs `Molecule` vs `Film`); others are layered (any mode can be combined with `Magnetism`, `TDDFT`, `Hubbard`, `SCF`, etc.).

## 2. Two electronic-structure engines

### Finite Difference Method (FDM) — default

- Solves the Kohn-Sham / Schrödinger equation on a 3D real-space grid inside a sphere of radius `Radius` around the absorber.
- No muffin-tin approximation — the potential is free-shape.
- Numerical: 4th-order finite differences by default (`iord 4`), grid spacing set by `adimp` (energy-dependent allowed; default ~0.25 Å).
- Sparse linear system → solved by **MUMPS** (default since March 2015). The parallel `fdmnes_mpi` binary built on llmbox uses parallel MUMPS 5.6.2.
- Slow. Run time grows steeply with `Radius` (roughly cubic plus solver overhead). Memory ditto.
- **Best for** low-symmetry / open structures, molecules, surfaces, pre-edge fine structure.

### Multiple-Scattering / Green's-function (MST) — keyword `Green`

- Muffin-tin potential, Green-formalism multiple scattering.
- Much faster, much less memory.
- Less precise for non-spherical environments.
- **Best for** the first pass on any new material — the manual explicitly recommends starting in MST and only switching to FDM once the structure / radius / multipoles / SCF are dialled in (see **pipelines.md** § "FDM vs MST comparison ladder").

The choice is binary: `Green` keyword present = MST; absent = FDM. Most other keywords work the same way under either engine.

## 3. DFT / TDDFT layer

- **Default exchange-correlation:** PBEGA (Perdew-Burke-Ernzerhof GGA potential with Hedin-Von Barth energy dependence). **Note:** this is a 2026-03-10 default change documented only in `FDMNES_Modifications.txt`; the manual still describes "real PBE96" as default (§ 6). To restore the pre-2026 LDA, use `Hedin` (Hedin-Lundqvist).
- Alternative XC: `Perdew` (Perdew-Wang), `Xalpha α` (Xα with explicit α; ~2/3 ≈ Hedin-Lundqvist), `Clementi` (Clementi-Roetti atomic functions).
- **SCF self-consistency** is opt-in (`SCF` keyword). Without `SCF`, the potential is built from superposed atomic densities. With it, the charge density is iterated until total energy converges to `Delta_E_conv` (default 0.1 × N_atoms eV) or `N_self` cycles (default 100). Mixing parameter `P_self` default 0.1.
- **Hubbard / DFT+U** via `Hubbard` (per-atom-type) or `Hubbard_z` (per-element). U-J in eV. Combine with `SCF` for sensible results. The manual notes DFT+U formally only applies to insulators.
- **TDDFT** via `TDDFT` (full Coulomb + XC kernel) or `TDDFT + RPA` (Coulomb-only kernel). Run as a *post-processing* step after the LSDA-level calculation finishes. `Lmax_tddft` caps the matrix dimension (default 2 for Z < 21, 3 otherwise; lower for optics).
- TDDFT improves L₂/L₃ branching at 3d-element edges and is required for sensible optical / dielectric spectra. It does **not** reproduce multiplet / excitonic features — those are out of DFT's reach.

## 4. Physical scope and stated limitations

From manual § B (advice, p. 11) and § C-V:

- DFT is in principle false for excited states. Agreement: K and L₁ edges of all Z, and L₂/L₃ of heavy elements (Z ≥ 31), typically reproduce intensity within ~10 % and position within a few eV.
- Multiplet / excitonic features in transition-metal oxides (e.g. the L₂,₃ multiplet structure of NiO) are **not** reproduced. Use a multiplet code (CTM4XAS, Quanty) for those.
- L₂,₃ branching ratio for early 3d at the LDA level is wrong; `TDDFT` partially fixes it.
- Half-core-hole option deliberately omitted — manual says "because the author does not understand what this means" (p. 13).
- For molecules in condensed phase, the asymptotic potential must be clamped with `Vmax` (typically `Vmax -6`) to prevent spurious bound states above the molecule.

## 5. Symmetry and equivalence

- Crystal symmetry: full space groups via `Spgroup` (international symbol or number; `Fd-3m:1` and `227:1` both accepted). Reads non-equivalent atoms only — but **only in non-magnetic mode**. For magnetic systems, give every atom explicitly.
- Cluster point-group symmetry is detected automatically; `Pointgrou` forces it and disables auto-detection; `Symmol` uses the molecular point group.
- **`Full_atom` / `SpGr_Atom` distinction** (this is the second 2026-03-10 default change):
  - **Default** (2026-03-10 onward): every absorber-equivalent class is built with its own atomic potential (point-group equivalence). More accurate, more memory.
  - **Legacy** (`SpGr_Atom` keyword): atoms equivalent by space-group share a potential. Cheaper but "*could be unstable*" — manual p. 50.
- Antiferromagnetism: prefix the atom-type index with `-` to flip the spin in `Crystal` / `Molecule` rows. Non-collinear: put a line of Euler angles above the atom in the structure block.
- Spin axis defaults to `c` (hexagonal c in trigonal cells). Override with `Axe_spin v_a v_b v_c` (vector in direct-lattice basis) or `Ang_spin α β γ` (Euler).

## 6. Multipolar transitions

Default: **E1·E1 only** (electric dipole · electric dipole). Enable higher orders explicitly. Source: `lecture.f90:2122` and the multipole flags at lines 3026-3094.

| Channel | Umbrella keyword | Fine-grain enable | Fine-grain disable |
|---|---|---|---|
| E1·E1 | (default) | `E1E1` / `Dipole` | `No_E1E1` |
| E1·E2 | `Quadrupole` (sets E2E2 path on, NOT the bilinear interference by itself) | `E1E2` | `No_E1E2` |
| E1·E3 | `Octupole` | `E1E3` | `No_E1E3` |
| E2·E2 | `Quadrupole` | `E2E2` | `No_E2E2` |
| E3·E3 | `Octupole` | `E3E3` | `No_E3E3` |
| E1·M1 | `Dipmag` | `E1M1` | — |
| M1·M1 | `Dipmag` | `M1M1` | — |
| E2·M2, E1·M2, M2·M2 | `Quadmag` | `E2M2`, `E1M2`, `M2M2` | — |
| E1·SP, SP·SP (spin-position) | `Dip_rel` | `E1SP`, `SPSP` | — |

Selection rules: `lplus1` restricts to Δl = +1; `lminus1` to Δl = −1.

Practical guidance from the manual: for K of 3d/4d/5d and for L₂,₃ of heavy elements, **always enable `Quadrupole`** for pre-edge fidelity. Adding `Dipmag` is necessary for L-edge magnetic systems (E1-M1 interference).

## 7. Edges and double edges

Selected by `Edge`. Accepts `K`, `K1`, `L1`, `L2`, `L3`, `M1`, `M2`, `M3`, `M4`, `M5`, `N1`-`N5`, `O1`-`O5`, and the **double edges** `L23`, `M23`, `M45`, `N23`, `N45` which compute both subshells in one run.

For double edges the convolution accepts two `Gamma_hole` values (one per subshell; first listed is the higher-j subshell, e.g. L₂ before L₃ for `L23`).

## 8. Defaults that recently changed (canonical list)

This is the master "watch out for these" table. Anything not in here is presumed stable across releases.

| Default | Old behaviour | New behaviour (≥ 2026-03-10) | Restore old with |
|---|---|---|---|
| Exchange-correlation potential | Hedin-Lundqvist (LDA) | **PBEGA** (GGA, Perdew-Burke-Ernzerhof gradient + Hedin-Von Barth energy dep.) | `Hedin` |
| Atomic equivalence in cluster | Space-group equivalence | **Full_atom** (point-group equivalence) | `SpGr_Atom` |
| `Gamma_max` (high-energy lifetime plateau) | 15 eV | **10 eV** | `Gamma_max 15` |
| MUMPS solver | optional | **default since March 2015** | — |
| Excited absorbing atom (core hole on absorber) | varied | **default** at K, L₁, M₁, O₁; non-excited default at L₂,₃, M₂,₃, M₄,₅ | `Excited` / `Nonexc` |
| SCF in-loop spin polarisation | pre-2012: free | **fixed total up/down counts** | `SCF_mag_free` |

(Source: `FDMNES_Modifications.txt` for the first two, manual § D for `Gamma_max`, manual § B for the others.)

## 9. Other notable physics-side conventions

- **Units throughout**: Å for lengths, eV for energies. Cross-section in **Mbarn** (1 Mbarn = 10⁻¹⁸ cm²), summed over all absorbers in the cell. `Per_atom` divides by absorber count for Mbarn/atom. FDMX `cm2g` overrides to cm²/g.
- **Diffraction intensities** in (number-of-electrons)².
- **Energy reference**: output energy is relative to the calculated Fermi level by default. `Energpho` switches to absolute photon-energy. `Epsii eV` anchors the initial-state reference (safer to set during convolution than during FDM).
- **Polarisation vectors** in `Polarize` are given in the *non-orthogonal direct-lattice basis* and auto-normalised. For non-cubic cells the literal numbers differ from a Cartesian intuition — see manual p. 23, including the explicit hexagonal formula.
- **DAFS azimuth basis**: `(I, J, Q)` with `I = (Q × c) / |Q × c|`, falling back to `I = (Q × a) / |Q × a|` if `Q ∥ c`. Counter-clockwise rotation is positive. `Zero_azim` and `Setaz` override the reference vector.

## 10. Pitfalls (theory-level)

- *Beating phenomenon* in SCF for oxides — energy oscillates with cluster radius. Workaround: fix the core-state reference with `Epsii` (read its value from a converged smaller-radius bav, then impose it).
- For partial occupancies (CIF-imported), atoms may overlap pathologically. Use `Occupancy` and let FDMNES build an Average-T-Matrix (default), or disable with `No_ATA`.
- Spurious bound states above molecules in solution → clamp with `Vmax -6`.
- For 1/3 / 2/3 fractional coordinates, supply ≥ 10 decimal digits — short forms cause "ghost" atoms or hard stops in symmetry detection.
- FDM grid can rotate to follow spin axis between two spin-direction runs → `Mag_axis_free` or finer `Adimp` to make the comparison meaningful.
- Default first-atom = absorber rule trips when CIF imports list by Wyckoff position rather than chemistry. Use `Z_absorber` explicitly.

See **inputs-and-outputs.md** for file-format details and **pipelines.md** for the canonical recipes that exercise each of these capabilities.
