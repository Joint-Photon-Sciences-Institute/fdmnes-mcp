---
date: 2026-05-19
project: fdmnes
type: docs-examples
---

# FDMNES — annotated example catalog

Reference for the bundled examples in `/home/nmarcella/fdmnes/linux_bundle/fdmnes_Linux/Sim/Test_stand/in/`. Companion to the [docs index](2026-05-19-docs-overview.md). When in doubt about an input, the nearest example here is usually a reliable starting point.

FDMNES inputs are line-based, free-format, comment-introduced with `!`, and read keyword blocks until `End`. The standard solver mode is **FDM** (finite-difference); presence of the `Green` keyword switches to **multiple-scattering (MS)** on a muffin-tin potential — that's the single most important distinguishing flag across these examples.

## 1. Basic XANES baselines

### `Cu_inp.txt` — Cu metal FCC, K-edge
- **System:** Copper metal, cubic FCC (a = 3.61 Å, Z = 29 at four positions). Cu K-edge XANES.
- **Demonstrates:** Minimal, canonical FDMNES input. Reference baseline every other example should be compared against. Comment: "*Calculation for the copper K-edge in copper cfc / Finite difference method calculation with convolution*".
- **Method:** FDM (no `Green` keyword).
- **Mode:** XANES.
- **Key keywords:** `Range`, `Radius 3.0`, `Crystal`, `Convolution`. (Comment notes radius should be 6-7 Å for production.)
- **Filout:** `Sim/Test_stand/Cu`

### `Cr_inp.txt` — Cr BCC, K-edge with DOS preparation
- **System:** Chromium metal, BCC (a = 2.8839 Å, Z = 24). Energy range extended to −90 eV for photoemission staging.
- **Demonstrates:** Photoemission setup; partial DOS via `Density`; complex energy `Eimag 0.2` to broaden atomic levels.
- **Method:** MS (`Green`).
- **Mode:** XANES + DOS (pre-stage for `Cr_conv` photoemission).
- **Key keywords:** `Eimag`, `Green`, `Density`, `Quadrupole`.
- **Filout:** `Sim/Test_stand/Cr`

### `GaN_inp.txt` — GaN hexagonal, Ga K-edge with DAFS
- **System:** Hexagonal GaN (a = 3.187, c = 5.186, γ = 120°). Ga K-edge.
- **Demonstrates:** In-plane diffraction at (110) with `Energpho` (absolute photon-energy axis) and atomic f', f'' tables.
- **Method:** MS.
- **Mode:** XANES + DAFS.
- **Key keywords:** `Energpho`, `DAFS 1 1 0 1 1 90.`, `Fprime`, `Fprime_ato`.
- **Filout:** `Sim/Test_stand/GaN`

## 2. SCF / electronic-structure refinement

### `Fe2O3_scf_inp.txt` — Hematite K-edge with self-consistent potential
- **System:** α-Fe₂O₃ (rhombohedral, 4 Fe + 6 O). Fe K-edge.
- **Demonstrates:** The `SCF` self-consistency loop on the charge density. Most important refinement over the bare `Fe2O3_inp` baseline.
- **Method:** MS.
- **Mode:** XANES + DAFS (two reflections: (111) σ-π and (222) σ-σ).
- **Key keywords:** `SCF`, `Quadrupole`, `Density`, `DAFS`.
- **Filout:** `Sim/Test_stand/Fe2O3_scf`

### `Fe2O3_hub_inp.txt` — Hematite with DFT+U Hubbard correction
- **System:** Same hematite cell as above.
- **Demonstrates:** DFT+U on Fe 3d. Drop-in identical to `Fe2O3_scf` except `SCF` replaced by `Hubbard 5.` (Ueff = 5 eV). Classic teaching pair: "what does +U do to the pre-edge?".
- **Method:** MS.
- **Mode:** XANES + DAFS.
- **Key keywords:** `Hubbard 5.`, `Quadrupole`, `Density`, `DAFS`.
- **Filout:** `Sim/Test_stand/Fe2O3_hub`

### `TiO2_lapw_inp.txt` — TiO₂ rutile, FLAPW potential import
- **System:** Rutile TiO₂, Ti K-edge.
- **Demonstrates:** Reading a converged Wien2k FLAPW potential from external files (`TiO2.struct`, `TiO2.vcoul`, `TiO2.r2v`, `TiO2.clmsum`, `TiO2.ti1s`) instead of building the potential internally. Uses `Trace` to project on the (1,1,0) direction.
- **Method:** FDM with externally supplied potential.
- **Mode:** XANES (`Quadrupole` enabled).
- **Key keywords:** `Flapw` + five external files, `Trace`, `Quadrupole`.
- **Filout:** `Sim/Test_stand/TiO2_lapw`

### `Ba2ZnUO6_inp.txt` — Double perovskite, O K-edge with custom atomic configs
- **System:** Ba₂ZnUO₆ ordered double perovskite (cubic, a = 8.39 Å). Oxygen K-edge.
- **Demonstrates:** Explicit ionic configurations via `Atom` block (U: 5f¹ 6d⁰; Ba: +1; Zn: +1), full relativistic potential (`Relativism`), and `State_all` to output unoccupied states too.
- **Method:** MS.
- **Mode:** XANES.
- **Key keywords:** `Atom` (custom electronic config), `State_all`, `Relativism`.
- **Filout:** `Sim/Test_stand/Ba2ZnUO6`

## 3. Magnetism / XMCD

### `Ni_mg_inp.txt` — Nickel L₂,₃, magnetic without spin-orbit
- **System:** Ni FCC, L₂ and L₃ edges. Custom `Atom 28 1 3 2 5. 3.` (3d⁵↑ 3d³↓).
- **Demonstrates:** Collinear magnetism (`Magnetism`) producing XMCD. Two polarisations: linear + circular `0 0 0 0 0 1`. No spin-orbit in the final state.
- **Method:** MS.
- **Mode:** XANES + XMCD.
- **Key keywords:** `Magnetism`, `Polarisation`, `Edge L23`, `Density`.
- **Filout:** `Sim/Test_stand/Ni_mg`

### `Ni_inp.txt` — Nickel L₂,₃, magnetic with spin-orbit
- **System:** Same as `Ni_mg_inp.txt`.
- **Demonstrates:** Paired counterpart — adds `Spinorbit` so SO appears in the final-state Hamiltonian. Teaching point: how SO shifts and splits the L₂/L₃ branching in XMCD.
- **Method:** MS.
- **Mode:** XANES + XMCD.
- **Key keywords:** `Spinorbit`, `Edge L23`, `Polarisation` (circular), `Density`.
- **Filout:** `Sim/Test_stand/Ni`

### `NdMg_inp.txt`, `NdMg_FDM_mg_inp.txt`, `NdMg_FDM_so_inp.txt` — non-collinear magnet trio
- **System:** Intermetallic NdMg, Nd L₂. Euler angles per site (`45 90`, `135 90`, `315 90`, `225 90`) define a canted Nd magnetic structure.
- **Demonstrates:** Three-way comparison on the *same* magnetic structure:
  - `NdMg_inp` — MS with `Spinorbite`. Production-grade.
  - `NdMg_FDM_mg` — FDM with `Magnetism` only (no SO). Coarse grid (`Adimp 0.3`, `iord 2`) — "just for test".
  - `NdMg_FDM_so` — FDM with `Spinorbite`. Coarse grid for speed.
- **Method:** MS vs FDM (paired comparison).
- **Mode:** XANES + magnetic DAFS (four reflections).
- **Key keywords:** Euler angles in `Crystal`, `Polarisation 0 0 1`, `Eimag 0.1` (MS), `Adimp`, `iord`.
- **Filout:** `Sim/Test_stand/NdMg`, `…/NdMg_FDM_mg`, `…/NdMg_FDM_so`

### `V2O3_inp.txt` — Antiferromagnetic V₂O₃ low-T monoclinic
- **System:** Monoclinic AFM V₂O₃ (8 V split into ±-spin chemical types, 12 O), V K-edge.
- **Demonstrates:** Tilted spin axis `Axe_spin -0.08909 0. -0.15025`; spherical-tensor decomposition (`Spherical`) on an RXS forbidden reflection.
- **Method:** MS.
- **Mode:** XANES + RXS (four polarisations on (111)).
- **Key keywords:** `Spinorbite`, `Axe_spin`, `Spherical`, `Density`, `Quadrupole`.
- **Filout:** `Sim/Test_stand/V2O3`

## 4. Multipoles beyond E1·E1

### `Fe3O4_inp.txt` — Magnetite K-edge, full multipole RXS
- **System:** Fe₃O₄ (Fd-3m, a = 8.394 Å), Fe K-edge, three DAFS reflections (002), (006), (444).
- **Demonstrates:** `Spgroup Fd-3m:1` symmetry-driven equivalence; `Atom_conf` overrides Fe 3d/4p populations on selected atoms. Both `Self_abs` and `Double_cor` post-processing corrections enabled.
- **Method:** MS.
- **Mode:** XANES + DAFS/RXS with E1-E1 and E2-E2.
- **Key keywords:** `Quadrupole`, `Self_abs`, `Double_cor`, `Atom_conf`, `Spgroup`.
- **Filout:** `Sim/Test_stand/Fe3O4`

### `Fe3O4_dd_inp.txt` — Magnetite, extracted tensors, E1E1 + E2E2 only
- **System:** Same Fe₃O₄.
- **Demonstrates:** Tensor-level reuse via `Extract Sim/Test_stand/Fe3O4_bav.txt`; explicit `E2E2` only (no E1E2 cross term). Pre-edge isolation. Comment: "*Iron K edge in magnetite, high temperature, without E1-E2*".
- **Method:** MS (reuse, not recomputed).
- **Mode:** RXS.
- **Key keywords:** `Extract`, `E2E2`, `Atom_conf`, `Self_abs`, `Double_cor`.
- **Filout:** `Sim/Test_stand/Fe3O4_E1E1_E2E2`

### `CuO_inp.txt` — Birefringence in CuO σ-σ RXS at L₂,₃
- **System:** Monoclinic CuO (Åsbrink-Waskowska 1991), Cu L₂,₃ edge. 32-atom unit cell with custom types ±1, 2 distinguishing inequivalent Cu and O.
- **Demonstrates:** Birefringence in σ-σ; `Full_Self_abs` for self-absorption including birefringence; circular polarisation; magnetic-dipole term via `Dipmag` (E1-M1 and M1-M1).
- **Method:** MS.
- **Mode:** RXS with E1-M1 / M1-M1 (σ-σ on (1 0 -1)).
- **Key keywords:** `Edge L23`, `Full_Self_abs`, `Dipmag`, `Circular`, `Double_cor`, `Spinorbite`, `Axe_spin 0 1 0`.
- **Filout:** `Sim/Test_stand/CuO`

### `AminoAcid_Optic_inp.txt` — L-isoleucine optical CD
- **System:** Organic crystal of L-isoleucine (C₆H₁₃NO₂). Nitrogen K-edge (`Z_absorber 7`).
- **Demonstrates:** Optical mode (`Optic`) with circular-dichroism from the E1·M1 cross term. Full multipole stack `E1E2 E2E2 E1M1 M1M1`. Uses `Perdew` LDA instead of default GGA.
- **Method:** FDM, with `SCF`.
- **Mode:** Optic / CD.
- **Key keywords:** `Optic`, `Perdew`, `E1E2 E2E2 E1M1 M1M1`, `Polarize` (circular triple).
- **Filout:** `Sim/Test_stand/AminoAcid_Optic`

## 5. RXS / DAFS detail and azimuthal scans

### `Fe2O3_inp.txt` — Hematite forbidden-reflection RXS (Finkelstein effect)
- **System:** Hematite, Fe K-edge.
- **Demonstrates:** Finkelstein effect on (111) σ-π forbidden reflection. Three reflections: (111) at fixed azimuth 0, (111) σ-π with *automatic azimuthal scan* (no azimuth supplied), (222) allowed. `Spherical` writes per-tensor contributions per reflection.
- **Method:** MS.
- **Mode:** XANES + RXS.
- **Key keywords:** `Spherical`, `Self_abs`, `Estart -20.`, `RXS` block, `Quadrupole`.
- **Filout:** `Sim/Test_stand/Fe2O3`

### `Ca3Co2O6_inp.txt` — Co K-edge in spin-chain cobaltite
- **System:** Rhombohedral Ca₃Co₂O₆ (R-3c:H, two Co sites). Co K-edge.
- **Demonstrates:** Azimuthal RXS scan (σ-π (1 3 1)) followed by inline use of `Selec_input`/`Selec_output` and `Energy 2.` to *select a single energy slice* in the same input.
- **Method:** MS.
- **Mode:** XANES + RXS azimuthal scan.
- **Key keywords:** `Polarise`, `Eimag 0.1`, `Selec_input`/`Selec_output`, `Energy`.
- **Filout:** `Sim/Test_stand/Ca3Co2O6`

### `Fe2O3_selec_inp.txt` — Standalone slice of a previous azimuthal scan
- **System:** Fe₂O₃, post-processing only.
- **Demonstrates:** Stripped-down selection step: reads convolved scan `Fe2O3_scan_conv.txt`, picks `Energy 1.`, writes `Fe2O3_scan_E1_conv.txt`. Teaches the post-process re-entry idiom.
- **Method:** none (utility).
- **Mode:** RXS slice.
- **Key keywords:** `Selec_inp`, `Selec_out`, `Energy`.
- **Filout:** `Sim/Test_stand/Fe2O3_scan_E1_conv.txt`

### `Fe3O4_Ag_2D_inp.txt` — Thin-film 2D resonant diffraction
- **System:** Fe₃O₄ film on Ag(001) bulk with Au cap layer (hexagonal cell).
- **Demonstrates:** Surface/interface RXS via `Film` / `Bulk` / `Cap_layer` block structure with per-layer thicknesses, roughnesses, B_iso, shifts. Specular truncation-rod scan `DAFS_2D` with operation-mode azimuth 0-180°. `Transpose_file` re-arranges convolved output to E × hk format.
- **Method:** MS.
- **Mode:** Surface RXS / CTR.
- **Key keywords:** `DAFS_2D`, `Film`, `Bulk`, `Cap_layer` + thickness/roughness/shift triplets, `hkl_film`, `Atom_B_iso`.
- **Filout:** `Sim/Test_stand/Fe3O4_Ag_2D`

### `Fe_bio_inp.txt` — DAFS from a PDB-described biological Fe site
- **System:** Iron in a protein/biological molecule, structure from `Fe_bio_struct.pdb`.
- **Demonstrates:** `pdb_file` import; experimental DAFS data from two files via `Dafs_exp` with orientation matrix and 30° re-orientation rotation; `Atom_conf` overrides only Fe atoms 6, 7, 11 in the PDB. `Gen_shift 7108 7118 11` scans E₀ across 11 trial values.
- **Method:** MS, `Memory_save`.
- **Mode:** DAFS with fit-to-data.
- **Key keywords:** `pdb_file`, `Dafs_exp` (orientation matrix), `Experiment`, `Z_absorber 26`, `Atom_conf`, `Gen_shift`, `Memory_save`.
- **Filout:** `Sim/Test_stand/Fe_bio`

## 6. Fitting to experiment

### `FeO6_inp.txt` — Octahedral FeO₆ molecule fit
- **System:** Isolated FeO₆ molecule (Fe at origin, 6 O at ±1 along axes; scaled by 2.16). Fe K-edge.
- **Demonstrates:** The full fitting workflow: `Molecule` cluster, `Experiment` file `FeO6_exp.txt`, `Gen_shift` scan for E₀, two `Parameter` blocks varying `Par_abc` (cell scale) and `Par_Gamma_max` (broadening). Canonical "two parameters + E-shift" fit.
- **Method:** MS.
- **Mode:** XANES fit.
- **Key keywords:** `Molecule`, `Experiment`, `Gen_shift`, `Parameter Par_abc`, `Parameter Par_Gamma_max`.
- **Filout:** `Sim/Test_stand/FeO6`

## 7. Convolution-only post-processing

### `VO6_conv_inp.txt` — Re-convolve a previous VO₆ run
- **System:** VO₆ result from `VO6_inp.txt`.
- **Demonstrates:** Pure convolution step. `Calculation` reads `VO6.txt` (not `Extract` — that's tensors). Tweaks `EFermi 2.0`, `Estart -15`, `Gamma_max 7.`. Writes renamed file `VO6_Ef20_GM7_conv.txt`.
- **Method:** none (post-process).
- **Mode:** Convolution-only.
- **Key keywords:** `Calculation`, `Convolution`, `EFermi`, `Gamma_max`, `Conv_out`.
- **Filout:** `Sim/Test_stand/VO6_Ef20_GM7_conv.txt` (via `Conv_out`)

### `Cr_conv_inp.txt` — Photoemission convolution of a previous Cr run
- **System:** Cr photoemission from `Cr_inp.txt` output.
- **Demonstrates:** Photoemission convolution (`Photoemission`) on `Cr.txt` with custom core-hole width `Gamma_hole 0.7`. The shortest input in the suite.
- **Method:** none (post-process).
- **Mode:** Convolution-only (photoemission).
- **Key keywords:** `Calculation`, `Photoemission`, `Gamma_hole`, `Conv_out`.
- **Filout:** `Sim/Test_stand/Cr_photo_conv.txt`

### `VO6_nodipole_inp.txt` — Extract tensors and turn off dipole
- **System:** Same VO₆ molecule.
- **Demonstrates:** Tensor-level reuse via `Extract Sim/Test_stand/VO6_bav.txt`, then `no_dipole` disables E1-E1 → only `Quadrupole` (E2-E2) contributes. Pre-edge isolation trick.
- **Method:** none (reuse).
- **Mode:** XANES E2-E2-only.
- **Key keywords:** `Extract`, `Quadrupole`, `no_dipole`, `Molecule`.
- **Filout:** `Sim/Test_stand/VO6_nodipole`

## 8. Special modes (TDDFT, NRIXS, FDMX, actinides, utilities)

### `VO6_inp.txt` — Vanadium VO₆ MS baseline
- **System:** Octahedral VO₆ molecule, V K-edge.
- **Demonstrates:** Simplest MS reference for the VO_* family (compared to FDM `Cu_inp.txt`). Writes DOS via `Density`, includes `Quadrupole`.
- **Method:** MS.
- **Mode:** XANES.
- **Key keywords:** `Green`, `Density`, `Quadrupole`, `Molecule`, `Estart -10.`
- **Filout:** `Sim/Test_stand/VO6`

### `VO6_tddft_inp.txt` — VO₆ L₂,₃ via TDDFT
- **System:** Octahedral VO₆, V **L₂,₃** edge.
- **Demonstrates:** TDDFT kernel via `TDDFT`, `SCF` to converge the ground state, `lmax 2` to throttle the spherical-harmonic expansion.
- **Method:** MS + TDDFT kernel.
- **Mode:** XANES (L-edge TDDFT).
- **Key keywords:** `TDDFT`, `SCF`, `Edge L23`, `lmax 2`, `Density`.
- **Filout:** `Sim/Test_stand/VO6_L23`

### `LiF_NRIXS_inp.txt` — Non-resonant inelastic X-ray scattering on LiF
- **System:** LiF rocksalt (Fm-3m, a = 4.0351 Å), F K-edge by default.
- **Demonstrates:** NRIXS / X-Raman. `NRIXS 3 6 9` sets three q-values (in Å⁻¹); `All_nrixs` outputs the full multipole decomposition at every q.
- **Method:** FDM, with `SCF`.
- **Mode:** NRIXS.
- **Key keywords:** `NRIXS`, `All_nrixs`, `SCF`, `Spgroup Fm-3m`, `Density`.
- **Filout:** `Sim/Test_stand/LiF_NRIXS`

### `Cu_FDMX_inp.txt` — FDMX extended-range absorption on Cu
- **System:** Cu FCC.
- **Demonstrates:** FDMX (high-energy / EXAFS-range extension to FDMNES; **K-edge only** per the comment). Energy range to 500 eV above edge with energy-dependent `Radius` and `Adimp` (cluster shrinks and grid coarsens with E). Atomic absorption tail via `Expntl 0.18 780.`; output in mass-absorption units via `Cm2g`.
- **Method:** FDM with FDMX extension.
- **Mode:** XANES → EXAFS bridge.
- **Key keywords:** `FDMX`, `Expntl`, `Cm2g`, E-dependent `Radius` and `Adimp`.
- **Filout:** `Sim/Test_stand/Cu_FDMX`

### `Pt13_inp.txt` — 13-atom Pt cluster, L₃-edge, one-run two-site
- **System:** Pt₁₃ cuboctahedral cluster (central Pt + 12 vertices), Pt L₃.
- **Demonstrates:** `One_run`: both inequivalent absorber sites (centre and surface) in one execution. `Center_abs` re-centres the cluster on the absorber; `Relativism` for heavy-atom physics; `Rmtg 1.7` overrides MT radius.
- **Method:** MS.
- **Mode:** XANES L₃.
- **Key keywords:** `One_run`, `Center_abs`, `Rmtg`, `Relativism`, `Edge L3`.
- **Filout:** `Sim/Test_stand/Pt13`

### `PuHClO4_VI_inp.txt` — Pu(VI) perchlorate, M₅ edge from CIF
- **System:** Pu(VI) HClO₄ perchlorate, Pu **M₅** edge. Structure read from CIF.
- **Demonstrates:** `Cif_file` import; actinide-edge with `Relativiste` and `Spinorbite`; absorber forced via `Z_absorber 94`.
- **Method:** MS.
- **Mode:** XANES M-edge.
- **Key keywords:** `Cif_file`, `Edge M5`, `Z_absorber 94`, `Relativiste`, `Spinorbite`, `Quadrupole`.
- **Filout:** `Sim/Test_stand/Pu_HClO4_VI_M5`

### `Mult_inp.txt` — Unit-cell multiplication utility
- **System:** Synthetic test cell, three atom types (Z = 26, 38, 33 via `Atomic_nu`).
- **Demonstrates:** `Mult_cell 2 2 1` utility to expand the unit cell along a, b. Uses `Unit_cell` rather than `Crystal`. Structural-preprocessing demo; no spectroscopy block.
- **Method:** utility.
- **Mode:** none.
- **Key keywords:** `Mult_cell`, `Atomic_nu`, `Unit_cell`.
- **Filout:** `Sim/Test_stand/Mult_out`

## Companion non-`_inp.txt` files (paired data)

- `Fe_bio_exp1.txt` — Experimental DAFS, 7 reflections (indices encoded as first 21 numbers on line 1). Paired with `Fe_bio_inp.txt`.
- `Fe_bio_exp2.txt` — Same format, ~150 reflections (much larger). Paired with `Fe_bio_inp.txt` at 30° azimuthal rotation per the input's `Dafs_exp` block.
- `Fe_bio_struct.pdb` — Truncated/fake PDB used for structure import; header literally says "*Fake pdb file for testing the FDMNES code*". Consumed by `pdb_file`.
- `FeO6_exp.txt` — Two-column XANES (eV, normalised µ) for `FeO6_inp.txt` fit.
- `Pu(VI)_HClO4.cif` — ICSD 421144, Pu(VI)O₂·5H₂O·2(ClO₄). Consumed by `Cif_file`.
- `TiO2.struct`, `TiO2.vcoul`, `TiO2.r2v`, `TiO2.clmsum`, `TiO2.ti1s` — Wien2k FLAPW dump for rutile (lattice/atoms, Coulomb pot, r²V, total charge density, Ti 1s core orbital). All five consumed by `TiO2_lapw_inp.txt`'s `Flapw` block.

## Recommended learning path

A new user should walk through these six in order. Each step adds exactly one new concept.

1. **`Cu_inp.txt`** — Run-and-look minimum. Learn the file layout (`Filout`, `Range`, `Radius`, `Crystal`, `Convolution`, `End`) and where FDM output lands. FDM baseline.
2. **`VO6_inp.txt`** — Same shape but `Molecule` instead of `Crystal`, `Green` for MS, `Density`, `Quadrupole`. FDM-vs-MS toggle and DOS output.
3. **`VO6_conv_inp.txt`** — Re-convolve previous results (`Calculation`, `Conv_out`, `EFermi`, `Gamma_max`). Post-processing idiom is essential before fitting.
4. **`Fe2O3_scf_inp.txt`** then **`Fe2O3_hub_inp.txt`** — Swap `SCF` for `Hubbard 5.`. Side-by-side comparison shows what self-consistency and DFT+U do to pre-edge and DAFS reflections.
5. **`FeO6_inp.txt`** — Introduces `Experiment` / `Gen_shift` / `Parameter` machinery on a tiny molecule with exp data. After this you have a complete forward-and-fit loop.
6. **`Ni_inp.txt`** (or `Fe3O4_inp.txt` for K-edge variant) — Adds magnetism: `Spinorbite`, circular `Polarisation`, XMCD output. At this point all major axes — solver, edge, multipole, magnetism, fit, post-process — have been touched.

After this baseline, the rest is a feature menu: `CuO_inp.txt` for E1-M1 birefringence, `LiF_NRIXS_inp.txt` for NRIXS, `Cu_FDMX_inp.txt` for the FDMX EXAFS bridge, `AminoAcid_Optic_inp.txt` for optical CD, `Pt13_inp.txt` for multi-site `One_run`, `PuHClO4_VI_inp.txt` for actinide M-edges from CIF, `TiO2_lapw_inp.txt` for FLAPW import, `Fe3O4_Ag_2D_inp.txt` for thin-film resonant diffraction, and `Fe_bio_inp.txt` for the heavy DAFS-from-PDB-with-experiment workflow.

## Notes on running these on llmbox

The bundled `fdmfile.txt` already points to `Sim/Test_stand/in/Cu_inp.txt` (single job). To run a different example, edit `fdmfile.txt` to list its `_inp.txt` path instead:

```
1
Sim/Test_stand/in/Fe2O3_scf_inp.txt
```

Then from `/home/nmarcella/fdmnes/linux_bundle/fdmnes_Linux`:

```
mpirun -np 4 /home/nmarcella/fdmnes/fdmnes_mpi
```

Most of these examples are small (FDM with `Radius 3 Å` or `Molecule` with a few atoms) — finishing in seconds to a couple of minutes. The exceptions are `Fe_bio_inp.txt` (heavy DAFS-from-PDB), `Fe3O4_Ag_2D_inp.txt` (surface), `LiF_NRIXS_inp.txt` (FDM + SCF), and `Cu_FDMX_inp.txt` (EXAFS-range). Don't expect linear scaling on the small ones — MPI overhead dominates. See [operations-on-llmbox.md](operations-on-llmbox.md) for the scaling reality.
