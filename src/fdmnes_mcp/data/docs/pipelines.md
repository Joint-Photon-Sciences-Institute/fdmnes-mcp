---
date: 2026-05-19
project: fdmnes
type: docs-pipelines
---

# FDMNES — workflow recipes

Companion to the [docs index](2026-05-19-docs-overview.md). Each section gives one concrete pipeline: what it's for, what keywords drive it, what files come out, what to watch for. Each links to the relevant bundled example in [examples-catalog.md](examples-catalog.md) when one exists.

The big-picture flowchart from manual p. 9: *parameter loop → XANES + DAFS amplitudes → convolution + DAFS intensities → experimental comparison → final spectra → azimuth/spectrum extraction*. Each stage is independently runnable from a previous stage's output.

## 1. Simple XANES first pass

Use when: first time looking at a new material.

```
Filout
   Sim/Cu/Cu_out
Range
   -2. 0.2 5. 0.5 10. 1. 40.
Radius
   3.0
Crystal
   3.610 3.610 3.610 90. 90. 90.
   29  0.0 0.0 0.0
   29  0.5 0.5 0.0
   29  0.5 0.0 0.5
   29  0.0 0.5 0.5
Green
Convolution
End
```

Keywords: `Filout`, `Range`, `Radius`, `Crystal`, `Green` (MS first), `Convolution`, `End`. That's it.
Files out: `Cu_out_bav.txt` (diagnostic), `Cu_out.txt` (unconvolved spectrum), `Cu_out_conv.txt` (convolved).
Gotcha: always check `*_bav.txt` first. The `Symsite` section confirms the space group; `Agregat` shows the built cluster, neighbours, distances. Pathological CIF imports show as overlapping atoms here.

Example: `Sim/Test_stand/in/Cu_inp.txt` (FDM variant) and `VO6_inp.txt` (MS variant).

## 2. FDM vs MST comparison ladder

The canonical "iterate until physics" workflow (manual § B p. 13). Run each step, inspect, only move on if the previous step looks sensible.

1. **MS, small radius**: `Green`, `Radius 3.0`.
2. **Relativism / SO**: add `Relativism` if any Z > 50; `Spinorbit` if conduction-band SO matters (heavy element, or L-edge magnetism).
3. **Tame the potential** (only for molecules in solution): `Vmax -6` to clamp asymptote.
4. **Increase radius**: 5 → 7 Å. Watch CPU/memory grow.
5. **Drop `Green` → FDM**: same input minus the `Green` keyword. Recompute.
6. **Add SCF**: `SCF` keyword. Watch the convergence trace in the bav file.
7. **Multipoles**: at K of 3d/4d/5d, or any L₂,₃ of heavy element, add `Quadrupole` for pre-edge fidelity. For L-edge magnetic, add `Dipmag`.

At step 5 (FDM), runtime explodes vs `Radius`. Use `Memory_save` if you hit a stack fault. The MUMPS-linked parallel binary is essential here — single-threaded FDM at 7 Å is hours to days.

## 3. SCF self-consistent, then spectrum

Use when: charge transfer is non-negligible (oxides, partially-ionic compounds), or the rising-edge shape is wrong after a non-SCF run.

```
SCF
N_self          ! optional
   50
P_self          ! optional, mixing fraction
   0.1
Delta_E_conv    ! optional, eV
   0.5
```

Add to a simple-XANES input. Files: bav file picks up an SCF convergence trace; ground-state cluster goes into `*_sd0.txt` and `*_sd1.txt` if `Density` is set.

Gotchas:
- "Beating phenomenon" in oxides: SCF energy oscillates with `Radius`. Workaround — converge at a smaller radius, read the resulting `Epsii` from the bav file, then impose it at larger radius via `Epsii <eV>`.
- SCF defaults to *non-excited* cluster at K, L₁, M₁, O₁ edges; *excited* at L₂,₃, M₂,₃, M₄,₅. Override with `Excited` / `Nonexc`.
- Use `Screening` together with `SCF_exc` for insulators.
- Default `N_self = 100`, `Delta_E_conv = 0.1 × N_atoms` eV, `P_self = 0.1`.

Example: `Sim/Test_stand/in/Fe2O3_scf_inp.txt`.

## 4. Convolution-only post-processing

Use when: you already have a `*_bav.txt` + `*.txt` from a previous job and want to re-broaden / re-shift without redoing the FDM/MST.

This is a *separate `_inp.txt`* containing only convolution keywords. The actual run is invoked the same way (`mpirun -np ... fdmnes_mpi` with an `fdmfile.txt` pointing at this input).

```
Calculation
   Sim/Test_stand/VO6
Conv_out
   Sim/Test_stand/VO6_Ef20_GM7_conv.txt
Convolution
EFermi
   2.0
Gamma_max
   7.
Estart
   -15
End
```

Keywords: `Calculation <prefix>` (the prior output's prefix, no extension), `Conv_out <new_path>` (output filename), `Convolution` (trigger the arctangent broadening), then any of `E_cut`, `EFermi`, `Gamma_max`, `Gamma_hole`, `Ecent`, `Elarg`, `Gaussian`, `Estart`, `S0_2`, `Selec_core`, `Sample_thickness`, `Abs_B_iso`, `Abs_U_iso`, `Per_atom`, `E_step_conv`.

Lifetime broadening model (manual p. 61): arctangent, Γ(E) = Γ_hole + Γ_max × [½ + (1/π) arctan( (π/3)(Γ_max/E_larg)(e − 1/e²) )], with e = (E − E_F)/E_cent. Three knobs: `Gamma_max` (high-E plateau, default 10 eV), `Ecent` (centre, default 30), `Elarg` (width, default 30). Alternative: `Seah A Gamma_m` for Seah-Dench inelastic.

Photoemission variant: replace `Convolution` with `Photoemission` (alias `XES`). Example: `Cr_conv_inp.txt`.

Tensor-level reuse (different mechanism): use `Extract <bav_prefix>` to read the unconvolved tensor and recompute the spectrum with different multipole channels, polarisation lines, or DAFS reflections. Example: `Fe3O4_dd_inp.txt`, `VO6_nodipole_inp.txt`.

## 5. EXAFS via FDMX

Use when: you want FDM accuracy out to typical EXAFS k-ranges (up to ~500 eV above edge).

```
FDMX
E_cut
   -1.5
```

The keyword `FDMX` **replaces** the explicit `Radius` schedule — FDMX picks an energy-dependent radius automatically (~8.3 Å up to 100 eV, then 7, 5, 4 Å at higher energies). Custom radius schedule still allowed.

Additional FDMX keywords (all read at top level in `main.f90`):
- `Gamma_hole`, `nohole` — core-hole lifetime / ground state
- `IMFPin <file>` — supply custom inelastic mean free path table
- `ELFin <file>` + `Mermin <order>` — compute IMFP from optical ELF
- `noIMFP` — disable IMFP broadening
- `Tmeas <K>`, `TDebye <K>`, `DWfactor <val>`, `noDW` — thermal disorder
- `noBG`, `Victoreen A B`, `Expntl A B` — atomic absorption background
- `cm2g` — output µ in cm²/g
- `FDMX_proc` — FDMX-only post-processing of a prior FDM run (skips the FDM calc)

Gotchas:
- **K-edge only is fully supported.** For other edges, you must supply `Gamma_hole` (or `nohole`) AND `noBG` explicitly.
- Without symmetry, the calc can take hours. Always run via the MUMPS-linked parallel binary.

Cite: Bourke, Chantler, Joly, *J. Synchrotron Rad.* **23**, 551 (2016).
Example: `Sim/Test_stand/in/Cu_FDMX_inp.txt`.

## 6. RXS / DAFS / azimuthal scans / forbidden reflections

Use when: anomalous elastic diffraction, including Templeton-style forbidden reflections.

```
DAFS
   1 1 1   1 1   0.      ! h k l, σ_in σ_out (codes), azimuth
   1 1 1   1 2           ! same hkl, σ-π, no azimuth → full scan
   2 2 2   1 1   0.      ! allowed reflection
Self_abs
Spherical
```

Polarisation codes: 1 = σ, 2 = π, 3 = circular right, 4 = circular left, 5 = linear general, 10 = scan over linear angles.

If azimuth is omitted on a row, FDMNES sweeps 0-360° at `Step_azim` (default 2°). Azimuth zero is set by `Zero_azim` (default `i_c` direction, or `i_a` if Q ∥ c). Reference reflection via `Setaz hkl`. `Phi_0` offsets the origin.

Modifiers:
- `Self_abs` — adds linear-absorption µ columns and self-absorption-corrected intensities (`Ic_*`).
- `Full_Self_abs` — full birefringence (requires σσ, σπ, πσ, ππ in that order). See `CuO_inp.txt`.
- `Double_cor` — double self-absorption correction.
- `Dead_layer <µm>`, `Surface_plane <hkl>`.
- `Forbidden` — zero out the Thomson f₀ term to isolate the resonant part.
- `Thomson <fr, fi pairs>` — impose non-resonant structure factors.
- `Fprime`, `Fprime_atom` — output Re/Im of scattering amplitude.
- `No_res_mag`, `No_res_mom` — multipliers on non-resonant magnetic scattering.

For analyser & Stokes parameters: `Mat_polar`, `Stokes`, `Stokes_name`, `Sample_thickness`, `Circular`, `Check_biref`, `Weight_co`.

Outputs: `X_scan.txt` (azimuth scan, unconvolved), `X_scan_conv.txt` (after convolution), `X_tr.txt` (rod scan at fixed energies if `Transpose_file` set), all the standard convolution outputs.

**Extracting a single slice from a finished scan** (Chapter F, separate run):
```
Selec_inp
   Sim/Test_stand/Fe2O3_scan_conv.txt
Selec_out
   Sim/Test_stand/Fe2O3_scan_E1_conv.txt
Energy
   1.            ! a single energy → slice gives intensity vs azimuth
Reflection
   2 5 6 9       ! pick reflections
End
```
Alternative: `Azimuth <values>` instead of `Energy` to slice the other way. See `Fe2O3_selec_inp.txt`.

Cite: Joly et al., *JCTC* **14**, 973 (2018).
Examples: `Fe2O3_inp.txt`, `Ca3Co2O6_inp.txt`, `Fe2O3_selec_inp.txt`, `Fe3O4_inp.txt`.

## 7. Surface / SRXRD / 2D resonant diffraction

Use when: surface-resonant XRD, crystal truncation rods, thin-film resonant diffraction, electrochemical interfaces.

Build a layered system (substrate to vacuum): `Bulk` → `Interface` (optional) → `Film` → `Surface` (optional) → `Cap_layer`. Each block has its own `*_shift`, `*_roughness`, `*_B_iso`/`*_U_iso`, and the cap also has `Cap_thickness`. Use `Mat_UB` to provide an explicit UB matrix; `Setaz` for azimuth reference.

```
DAFS_2D
   1 0 1   2   1 1   0. 0. 0. 0. 0. 0. 0.    ! hkl, operation-mode, polarisations, fixed angles
```

`DAFS_2D` uses a You-style 6-circle diffractometer operation mode + fixed-angle pattern. `hkl_film` switches indexing from bulk (default) to film basis; `hkl_int` to interface.

Speed-up flags (essential for big surface systems): `No_SCF_bulk` (skip SCF for bulk), `Green_bulk` (use MST for bulk), `Bulk_atom_not_recalculated` (lock bulk atoms).

Electrochemistry extensions: `Helmholtz V Δ width` (or `Helm_cos`, `Helm_mix`) imposes a double-layer potential; `Counter_atom` places probe atoms at fixed offsets above the surface; `Charge_image` adds a Coulombic image potential in vacuum.

Outputs: standard `X.txt` + `X_conv.txt`, plus rod scans via `Transpose_file`. `No_analyzer` to get σ+π sum directly.

Example: `Fe3O4_Ag_2D_inp.txt`.

## 8. XMCD / magnetic spectroscopy

Use when: ferro/antiferro/ferri systems; circular dichroism; Kerr/Faraday rotation; orbital moments.

Required combination:
1. **Either** `Magnetism` *or* `Spinorbit` (mandatory at K/L₁ where the XMCD signal vanishes without conduction-band SO).
2. **Per-spin orbital occupancies** in `Atom` or `Atom_conf` — double the occupancy columns (up, then down).
3. **Spin axis**: default `c` (or hexagonal `c` in trigonal). Override:
   - `Axe_spin v_a v_b v_c` (vector in direct-lattice basis, auto-normalised)
   - `Ang_spin α β γ` (Euler angles around z, new y, new z)
   - For non-collinear: prefix the atom row in `Crystal` with a line of Euler angles
   - Antiferromagnetism: prefix atom-type index with `-`
4. **Circular polarisation** in `Polarize`: e.g. `0 0 0 0 0 1` → x+iy and x−iy components → sum/difference columns in the output.

For comparison runs between different spin directions, use `Mag_axis_free` to prevent the FDM grid rotating with the spin axis. Without it, naive Adimp gives grid-induced numerical differences between spin orientations.

Gotcha: `Spinorbit` is 4-8× slower and ~2× more memory than `Magnetism` alone. For non-spin-orbit XMCD at L₂,₃, the manual recommends `Magnetism + Spinorbit` together.

Examples: `Ni_inp.txt` (with SO), `Ni_mg_inp.txt` (without SO), `NdMg_*_inp.txt` (non-collinear trio), `V2O3_inp.txt` (AFM monoclinic with tilted spin axis), `Fe3O4_inp.txt` (E1+E2+E1E2 magnetic).

## 9. Hubbard / DFT+U

Use when: localised d/f shells (Mott insulators, rare-earth oxides). Manual notes DFT+U is *formally* only sensible for insulators.

```
Hubbard
   5.        ! U-J in eV, per atom-type (order of Atom table)
SCF
```

Two variants:
- `Hubbard <U₁> <U₂> ...` — per atom-type, in the order of the `Atom` table.
- `Hubbard_z` rows of `Z V` — per element.

Typically combine with `SCF`. Comparison teaching pair: `Fe2O3_scf_inp.txt` vs `Fe2O3_hub_inp.txt` (identical except `SCF` ↔ `Hubbard 5.`).

## 10. TDDFT

Use when: 3d L₂,₃ edges (improves branching ratio), heavy-element edges, or optical/dielectric response.

```
TDDFT
SCF                     ! recommended ground state
Lmax_tddft
   2                    ! cap matrix size; lower for optics
```

Kernel choices:
- `TDDFT` alone — full kernel (Coulomb + XC).
- `TDDFT + RPA` (alias `RPALF`) — Coulomb-only.
- `Dyn_eg` / `Dyn_g` — diagonal-kernel variants.
- `Kern_fac <factor>` — scale the kernel; `Kern_fast` — fast variant.
- `Gamma_tddft` — apply lifetime broadening at TDDFT level.

TDDFT runs *on top of* the LSDA-level calc (which runs first). Outputs:
- `X_tddft.txt` — TDDFT XANES
- `X_tddft_scan.txt` — TDDFT azimuthal scan (with `DAFS`)
- `X_tddft_conv.txt` — convolved TDDFT spectrum

Defaults: `Lmax_tddft = 2` for Z < 21, `3` otherwise. Lower it explicitly for optics.

**Limitation**: TDDFT does NOT reproduce true multiplet / excitonic features. For those, use a multiplet code (CTM4XAS, Quanty).

Example: `VO6_tddft_inp.txt`.

## 11. NRIXS / X-Raman

Use when: high-q non-resonant inelastic scattering; X-Raman; bulk-sensitive XAS-like spectroscopy without core-hole effects.

```
NRIXS
   3.  6.  9.        ! |q| values in Å⁻¹ (powder average)
All_nrixs            ! optionally output full multipole decomposition
Lmax_nrixs
   2                 ! default ℓ-max for exp(iq·r) expansion
```

Monocrystal variant: `NRIXS_mono` with rows of `|q| qx qy qz`.

Output: `X_nrixs.txt` (replaces `X.txt`) — one column per q-value or per direction.

Cite: Joly, Cavallari, Guda, Sahle, *JCTC* **13**, 2172 (2017).
Example: `LiF_NRIXS_inp.txt`.

## 12. Optical / dielectric

Triggered with `Optic`. Useful range: visible / UV. Often combined with `TDDFT` and lowered `Lmax_tddft 2`.

For optical circular dichroism, enable `E1M1` (E1·M1 cross term).

Example: `AminoAcid_Optic_inp.txt` (L-isoleucine N K-edge optical CD with full `E1E2 E2E2 E1M1 M1M1` multipole stack and `Perdew` XC).

## 13. Fitting to experimental data

Use when: tuning convolution parameters and/or structural parameters to match measured XANES / DAFS.

```
Experiment
   FeO6_exp.txt   2     ! file + column for sigma channel (3, 4 columns for more)
Gen_shift
   -5. 5.  21          ! E0-shift scan: from −5 to +5 eV in 21 steps
Metric_out
   FeO6_fit.txt
Parameter
   Par_abc      0.95 1.05 11        ! scan cell scale 0.95...1.05 in 11 steps
Parameter
   Par_Gamma_max  5. 12. 8          ! independent scan
```

Confidence metrics:
- **D1** (default): metric distance, normalised.
- **D2** with keyword `D2`.
- **Rx** (Zanazzi-Jona R-factor) with keyword `Rx` / `fit_rx`.
- **Rxg**: grouped R-factor (`Rxg` followed by rows of spectrum indices).
- `Error` adds inverse-variance weighting if exp data has a 3rd column.

Parameters listed under the **same** `Parameter` block are correlated (moved together via the trailing `indice`). Different blocks are scanned independently → grid grows multiplicatively.

Available `Par_*` names (handlers in `lecture.f90:4709-4779`, `convolution.f90:323-364`, `metric.f90`):

| Class | Parameters |
|---|---|
| Convolution | `Par_ecent`, `Par_elarg`, `Par_e_cut`, `Par_gamma_hol`, `Par_gamma_max`, `Par_gaussian`, `Par_abs_u_iso`, `Par_aseah`, `Par_bseah` |
| Per-spectrum | `Par_shift`, `Par_weight`, `Par_weight_co` |
| Cell | `Par_a`, `Par_b`, `Par_c`, `Par_abc`, `Par_anga`, `Par_angb`, `Par_angc` |
| Atom positions | `Par_dposx`/`y`/`z`, `Par_posx`/`y`/`z`, `Par_theta`, `Par_phi` |
| Electronic | `Par_poporb`, `Par_occup` |
| Helmholtz | `Par_v_helm`, `Par_delta_hel`, `Par_width_hel` |
| Counter-atom | `Par_cato_*`, `Par_cdip_*`, `Par_cion_*` (positions/charge/width) |

Outputs:
- `X_fit.txt` — per-shift metric values.
- `Metric_out` file — full parameter-scan metric grid.
- `fdmfit_out.txt` — when fitting from convolution-only mode.

Examples: `FeO6_inp.txt` (small molecule, 2 params + E-shift), `Fe_bio_inp.txt` (heavy DAFS-from-PDB-with-experiment workflow).

## 14. Extraction (reuse previous calculations)

Three distinct mechanisms — pick the right one:

| Mechanism | What it reuses | When to use |
|---|---|---|
| `Calculation <prefix>` in a convolution-only job | The pre-convolved `X.txt` file | Re-broaden / re-shift only |
| `Extract <bav_prefix>` in a main `_inp.txt` | The unconvolved tensors stored in `X_bav.txt` | Add extra polarisations / DAFS reflections / multipole channels / DOS / TDDFT, without redoing FDM |
| `Selec_inp` / `Selec_out` (Chapter F mode) | A finished DAFS scan output | Pull spectra at fixed azimuth, or scans at fixed energy |

`One_run` / `One_run_s` is a separate optimisation that runs all absorbers in a single FDM sweep — cheaper but approximate (since the absorbing atom should formally differ from non-absorbers). Use `One_run` when comparing many sites where exact treatment isn't critical.

Examples: `VO6_conv_inp.txt` (`Calculation` re-convolve), `Fe3O4_dd_inp.txt` and `VO6_nodipole_inp.txt` (`Extract` reuse), `Fe2O3_selec_inp.txt` (`Selec_*`).

## 15. RIXS (2D maps)

Use when: resonant inelastic X-ray scattering 2D maps (incident energy × loss energy).

Triggered by `RIXS` + an incident-energy grid via `Energ_rixs`. The keyword combines emission with absorption; the manual doesn't dedicate a chapter to it, but the source `lecture.f90:252-296, 4443-4456` parses RIXS lines as q-vectors. `Theta_2theta` adds (θ, 2θ) pairs for RIXS scans; `Delta_g_r` sets RIXS Gaussian width; `Moment_conservation` is a recent (post-2025) momentum-conservation correction.

For valence-to-core emission (the "out" leg of RIXS), use `XES` (alias `Photoemission`) in a convolution-only run — see manual p. 63.

No bundled example for full RIXS 2D maps in this release. Compose XAS + XES manually for now.

## 16. Unit-cell modification (Chapter G)

Standalone utility for supercell construction. Not a spectroscopy mode.

```
Mult_cell
   2 2 1
Atomic_nu
   26 38 33      ! Z for each atom type
Unit_cell
   ! ... cell description ...
End
```

Keywords: `Mult_cell <na nb nc>` (multiply unit cell), `Cub_hexa` (cubic → hexagonal transform), `Mat_mul` (3×3 multiplication matrix), `Unit_cell` (replaces `Crystal` in this mode), `Surf_cell` (surface variant), `Atomic_nu` (assign Z per type).

**Source unclear**: the `mult_cell` subroutine that handles these keywords is not in the visible Fortran tree of the source release. Defer to manual § G.

Example: `Mult_inp.txt` (synthetic test case).

## Pipeline overview at a glance

```
Run mode                          Key keywords                      Files out
─────────────────────────────────────────────────────────────────────────────────────
Simple XANES                      Crystal/Molecule + Radius +       X.txt, X_conv.txt,
                                  Green + Convolution                X_bav.txt
SCF then spectrum                 ... + SCF [+ N_self + P_self]     ... + SCF trace in bav
FDM/MS ladder (steps 1-7 above)   Drop Green at step 5              same; CPU/RAM up
Convolution-only                  Calculation <prefix> + Conv_out + new conv file
                                  Convolution + (Γ knobs)
EXAFS / FDMX                      FDMX + E_cut + Gamma_hole          standard, extended E
RXS / DAFS                        + DAFS (reflection rows)           X_scan.txt
+ azimuth scan                    + (no azimuth on DAFS row)         X_scan_conv.txt
+ slice                           Selec_inp/out + Energy/Reflection  new sliced file
Surface SRXRD                     Bulk + Film + (Cap_layer) +        + rod scan via
                                  DAFS_2D + Mat_UB                   Transpose_file
XMCD                              Magnetism|Spinorbit + Atom (per-   sum/diff columns
                                  spin occ) + Polarize circular
DFT+U                             Hubbard <U-J> + SCF                + altered pre-edge
TDDFT                             TDDFT [+ RPA] + SCF +              + X_tddft*.txt
                                  Lmax_tddft
NRIXS                             NRIXS <q list> + All_nrixs +       X_nrixs.txt
                                  Lmax_nrixs (no X.txt)
Optic / CD                        Optic + (often TDDFT) + E1M1       optical spectra
Fit                               Experiment + Gen_shift +            X_fit.txt,
                                  Parameter <Par_*> blocks + Rx       Metric_out file
Extract (tensors)                 Extract <bav_prefix>                spectra w/o redo
Re-convolve                       Calculation <prefix> + Conv_out    cheap re-broaden
Extract (DAFS slice)              Selec_inp/out + Energy/Azimuth      slice files
```

## What's NOT in this docset (and why)

- **Beam-line-specific normalisation** — out of scope; do that in your post-processing (Larix, Larch, Xas Viewer).
- **Multiplet calculations** — FDMNES is single-particle; use CTM4XAS / Quanty for multi-determinant electronic structure.
- **Half-core-hole option** — deliberately not in FDMNES (manual p. 13).
- **Lattice dynamics, phonon DOS** — not in FDMNES.

For any of those, FDMNES output is just the input to your downstream tool.
