---
date: 2026-05-19
project: fdmnes
type: docs-io
---

# FDMNES — input and output files

Companion to the [docs index](2026-05-19-docs-overview.md). What FDMNES reads, what it writes, and how each file is structured. Lookups: the keyword list lives in [keyword-reference.md](keyword-reference.md); the workflows that drive these I/O patterns are in [pipelines.md](pipelines.md).

## 1. The master `fdmfile.txt`

When the executable starts it reads `fdmfile.txt` in the **current working directory** (not the directory of the binary). Format:

```
! comments start with !
<N>                              ! number of independent jobs to run
path/to/job1_inp.txt
path/to/job2_inp.txt
...
```

- Comments and blank lines are ignored.
- Paths are relative to the cwd of the running process.
- `N` is the count of jobs that follow; lines beyond `N` are ignored.
- Each job is independent — they run sequentially as if the program were re-invoked.

The bundled `linux_bundle/fdmnes_Linux/fdmfile.txt` is set up to run a single job (`Sim/Test_stand/in/Cu_inp.txt`); commented-out lines below it form a menu of other test inputs.

## 2. The job input file `<job>_inp.txt`

### 2.1 Grammar

- Line-oriented, free-form, case-insensitive.
- Comments: any line starting with `!`. Blank lines are ignored.
- A **block** is a keyword on its own line, followed by 0 or more value lines that the parser consumes for that keyword.
- Keywords are matched on their first 9 characters (`character(len=9) :: keyword` in `lecture.f90:152`). The manual and examples use full spellings; both work as long as the 9-character prefix is unique.
- Many keywords have aliases — see `Traduction()` at `main.f90:1884-2247` for the full list. Examples: `Crystal` = `Crist` = `Cryst` = `Cristal` = `Cristallo`; `Polarize` = `Polarise` = `Polar` = `Polarised`; `Spinorbit` = `Spin_orbi`; `EFermi` = `E_cut`.
- Reading **stops** at the keyword `End` (alias `Fin`). Anything after is silently ignored — useful for stashing scratch text at the bottom of a file.
- `Jump ... Endjump` brackets out a region of the input (a comment-out-block mechanism).
- Numbers are space-separated. **No tabs, no commas.**

### 2.2 The minimum viable input

A run needs exactly two blocks: one structure description (`Crystal` / `Molecule` / `Film` / `Surface` / a `Cif_file` / a `Pdb_file`) and `Radius`. Everything else has defaults. The canonical minimum from manual § C-I:

```
Filout
   Sim/Cu/Cu_out

Range
   -2. 0.2 5. 0.5 10. 1. 40.       ! E0 dE E1 dE E2 dE Emax (Å, eV)

Radius
   3.0

Crystal
   3.610 3.610 3.610 90. 90. 90.   ! a b c (Å) α β γ (deg)
   29  0.0 0.0 0.0
   29  0.5 0.5 0.0
   29  0.5 0.0 0.5
   29  0.0 0.5 0.5

Convolution

End
```

### 2.3 Structure-block formats

- **`Crystal`** — line 1: 6 reals (a, b, c, α, β, γ) in Å and degrees. Then one line per atom: `Z x y z` in fractional coordinates. Variants `Crystal_t`, `Film_t`, `Molecule_` read additional thermal/occupancy columns. `Atom_B_iso` / `Atom_B_ani` / `Atom_U_iso` / `Atom_U_ani` set the expected column layout.
- **`Molecule`** — same shape but coordinates are Cartesian (Å). With only 2 cell numbers → cylindrical (a, c) with positions (r, φ, z). With only 1 → spherical with (r, θ, φ).
- **`Film` / `Surface` / `Interface` / `Cap_layer` / `Bulk`** — stackable layers for surface/SRXRD problems. Each can carry its own `*_shift`, `*_roughness`, `*_thickness`, `*_B_iso`. The build order from substrate to vacuum: `Bulk` → `Interface` → `Film` → `Surface` → `Cap_layer`.
- **`Cif_file <name>.cif`** — import from CIF. Reads space group, lattice, atoms, optionally occupancy and B/U. `.cif` extension auto-appended.
- **`Pdb_file <name>.pdb`** — import from PDB (CRYST1, SCALE1, ATOM/HETATM). Sets `Occupancy=.true.`. Useful for protein active-site work.
- **`Flapw <files>`** — import a converged Wien2k FLAPW potential (replaces internal potential build). Five files: `.struct`, `.vcoul`, `.r2v`, `.clmsum`, `<element>.ti1s`. Variants for save/reload (`Flapw_s`, `Flapw_r`), new format (`Flapw_n`), with wavefunctions (`Flapw_psi`).

Atom rows after the lattice line take an integer in column 1: either Z (when no `Atom` block is present) or an atom-type index (1, 2, 3…) when an `Atom` block defines custom electron configurations. Negative atom-type index = spin-flipped (antiferromagnetism).

### 2.4 Absorber selection

Default: every atom of the species of the first row in the structure block is an absorber; their spectra are summed. Override mechanisms:

- **`Z_absorber 26 29`** — restrict by atomic number(s). All atoms with those Z become absorbers.
- **`Absorber 3 7`** — specific site indices. Outputs gain `_3` / `_7` suffixes.
- **`Allsite`** — every absorber gets its own output file (`X_atoma_*.txt`).

### 2.5 Energy ranges

- **`Range Emin dE1 E1 dE2 E2 ... Emax`** — variable-step energy grid. **Odd number** of values required; default is `-5 0.5 60`. Hard error on even count (`lecture.f90:341`).
- **`Rangel`** — like `Range` but logarithmic step rule (constant-k spacing).
- **`Energpho`** — output energies as absolute photon energies (not Fermi-relative).
- **`Epsii <eV>`** — anchor initial-state energy reference. Safer applied during convolution than during FDM.

## 3. The `Filout` / file-name convention

`Filout` (alias `File_out`, `Fileout`) takes one argument: the **output prefix** without extension, optionally with a relative directory. Default: `fdmnes_out` (working directory). All output files share this prefix and pick up automatic suffixes (`.txt`, `_conv.txt`, `_bav.txt`, etc.).

Example: `Filout Sim/Test_stand/Cu` → output files at `Sim/Test_stand/Cu.txt`, `Sim/Test_stand/Cu_conv.txt`, `Sim/Test_stand/Cu_bav.txt`, etc.

The directory must exist — FDMNES will NOT create it. (Standard pre-flight: `mkdir -p Sim/Test_stand/` before running.)

## 4. Output files (catalog)

For a job with `Filout X`:

### 4.1 Always written

| File | Content | Notes |
|---|---|---|
| `X_bav.txt` | "Talkative" log: release date, structure echo (Symsite), built cluster (Agregat), point group, neighbour shells, potential, Fermi level, SCF cycles, convolution curve. | **Inspect this first** when debugging. Pathological positions or wrong neighbour distances are visible immediately. Size grows fast with cluster — 1+ MB common. |
| `X.txt` | The unconvolved spectrum: energy column + one cross-section column per `Polarize` line + powder average. | Mbarn per cell. Use `Per_atom` to get Mbarn/atom. |
| `X_nrixs.txt` | NRIXS-only spectra (when `NRIXS` used). Replaces `X.txt`. | One column per q-value or per direction. |

### 4.2 On `Convolution` / convolution-only job

| File | Content |
|---|---|
| `X_conv.txt` | Convolved spectrum (Lorentzian + optional Gaussian). For RXS: reflection intensities. |
| `X_scan_conv.txt` | Convolved azimuthal scan (when `DAFS` ran a scan). |
| `X_tr.txt` | Transposed DAFS (rod scan at fixed energies — from `Transpose_file`). |
| `<your_Conv_out>` | If the convolution job sets `Conv_out path/file.txt`, the output goes there instead of the default `X_conv.txt`. Used for renaming when re-convolving the same source. |

### 4.3 On `Density` / `State_all` / `Allsite`

| File | Trigger | Content |
|---|---|---|
| `X_sd0.txt` | `Density` | Projected DOS, ground-state cluster (no core hole). Energy + per-(l,m) DOS columns. |
| `X_sd1.txt` | `Density` | Projected DOS, excited cluster (core hole on absorber). |
| `X_sda.txt` | `Density_a` | Density at all sites (one set per non-equivalent site). |
| `X_sdi.txt` (i = atom index) | `Density_all` | pDOS for every atom of the cluster individually. |
| `X_atoma.txt` (a = absorber index) | `Allsite` | Spectra resolved per non-equivalent absorbing atom. |
| `X_atoma_scan.txt` | `Allsite` + `DAFS` | DAFS azimuth scan per absorber. |

### 4.4 On `DAFS` / `RXS`

| File | Trigger | Content |
|---|---|---|
| `X_scan.txt` | `DAFS` with no fixed azimuth | DAFS amplitudes vs azimuthal angle (default 2°step; `Step_azim` to change). |
| `X.txt` columns | `DAFS` | Adds reflection columns: real/imag scattering amplitude per reflection, then intensities after convolution. |
| `Ic_*` columns | `Self_abs` | Self-absorption-corrected intensities. |
| `mu_*` columns | `Self_abs` | Linear absorption coefficients (µm⁻¹). |

### 4.5 On `TDDFT`

| File | Content |
|---|---|
| `X_tddft.txt` | TDDFT-level XANES spectrum. |
| `X_tddft_scan.txt` | TDDFT-level azimuthal scan. |
| `X_tddft_conv.txt` | Convolved TDDFT spectrum. |

The non-TDDFT files (`X.txt`, `X_scan.txt`, `X_conv.txt`) are also written — TDDFT runs on top of the LSDA calculation.

### 4.6 On `Spherical` / `Sphere_all` / `Cartesian`

Tensor decomposition outputs. The full list (from manual p. 16):

| File | Content |
|---|---|
| `X_sph_atoma.txt` | Spherical tensor per absorbing atom. |
| `X_sph_atoma_int.txt` | Integrated form. |
| `X_sph_xtal.txt` | Crystal-summed spherical tensor. |
| `X_sph_xtal_int.txt` | Integrated. |
| `X_sph_xtal_rxsi.txt` | RXS reflection i. |
| `X_sph_signal_atoma_xan.txt` | XANES signal per atom. |
| `X_sph_signal_atoma_poli.txt` | Per polarisation i. |
| `X_sph_signal_atoma_rxsi.txt` | Per RXS reflection i. |
| `X_sph_signal_xtal_xan.txt` | Crystal-summed XANES signal. |
| `X_sph_signal_xtal_rxsi.txt` | Crystal-summed RXS signal. |
| `X_car_atoma.txt`, `X_car_xtal.txt`, `X_car_xtal_rxsi.txt` | Same in Cartesian basis (when `Cartesian` is set). |

### 4.7 On `COOP`

| File | Content |
|---|---|
| `X_<file>_coop_n_m.txt` | Crystal-orbital overlap population between atom indices n and m. |

### 4.8 On `Trace`

| File | Content |
|---|---|
| `X_trace.txt` | Potential / density along a 1D line. |
| `X_den.cube`, `X_pot.cube` | Density / potential on a 3D grid in Gaussian `.cube` format (open with VMD, VESTA, ParaView). |

### 4.9 On `Parameter` / `Experiment` (fit mode)

| File | Content |
|---|---|
| `X_fit.txt` | Per-shift metric values (D1 default; D2 with `D2`; Rx with `Rx`). |
| `<Metric_out value>` | If `Metric_out` is set, the parameter-scan metric grid goes there. Useful when scanning many parameters. |
| `fdmfit_out.txt` | Created when fitting from convolution-only mode. |

### 4.10 FDMX-specific

| File | Content |
|---|---|
| `X_ELF.txt` | Energy- and momentum-dependent ELF (when `ELFin` + `Mermin`). |

### 4.11 On failure

| File | Content |
|---|---|
| `fdmnes_error.txt` | Diagnostic line. Always check if the job ended unexpectedly. |

## 5. Column conventions

- **First column**: photon energy (eV). Default = Fermi-relative; absolute if `Energpho` was set; loss-energy if NRIXS.
- **Subsequent columns**: cross-section per polarisation in Mbarn, in the order they appear in `Polarize`, plus the powder average. Cell-summed by default; `Per_atom` divides by absorber count.
- **DAFS columns**: when `Fprime` is set, each `DAFS` line contributes a triple `(f', f'', I)`; without `Fprime`, two columns `(f', f'')`. With `Self_abs`, an extra `µ` column per polarisation. With convolution, intensities post-self-abs picked up with prefix `Ic`.
- **Headers** contain parentheses by default. Set `Python` keyword to get underscores for plot-parser friendliness.
- **`Header`** keyword adds a metadata header (FDMNES release, date, convolution parameters, edge energy) readable by Xas Viewer / Larix.

## 6. Special parsing rules / pitfalls

1. **Odd-count rule**: `Range`, `Adimp`, `Radius` reject even-numbered argument lists with a hard stop. Always supply odd-count for energy-dependent sequences. (Single-value forms are fine.)
2. **9-char truncation collision risk**: keywords sharing a 9-char prefix collide. Known: `Crystal_t` (thermal) vs `Crystal_c` (CIF redirect). If you spell something exotic, check the canonical name in [keyword-reference.md](keyword-reference.md).
3. **Comment between block keyword and value**: the parser consumes value lines starting immediately after the keyword. Comments are skipped, but be aware that a stray comment with the wrong number of numeric tokens will throw off line-counted parses (especially the multi-line `Range`).
4. **`End` is mandatory.** Lines after `End` are ignored — including stray copies of keywords. If your job fails silently without converging, check that you don't have a missing `End` between concatenated inputs.
5. **Working directory** matters: `Filout` paths and `Calculation` / `Extract` filenames are relative to the cwd of the executable, not the cwd of `mpirun`. On Linux, paths are case-sensitive.
6. **CIF gotcha**: partial occupancies can produce atoms-too-close-together. Either tidy the CIF or use the default Average-T-Matrix (`No_ATA` to disable).
7. **Memory failures** present as silent hangs or stack faults without `fdmnes_error.txt`. Enable `Memory_save` for low-symmetry materials with many non-equivalent atoms.

## 7. Reading the bav file (diagnostics)

Sections in order (manual p. 12):

1. Release banner and date.
2. Echo of input file as parsed.
3. **`Symsite`** — space-group info, list of non-equivalent atoms with multiplicities. Check this matches your CIF.
4. **`Agregat`** — built cluster around each absorber: point group, neighbours grouped by shell with distances. Pathological CIF imports show here as overlapping atoms.
5. Potential build log, Fermi-level search.
6. SCF cycles (if `SCF`): energy, charge, magnetic moment per atom per iteration.
7. Per-energy spectrum log.
8. Convolution params and the chosen Γ(E) curve.
9. Total CPU time.

If a run looks wrong, the first 30 lines of `X_bav.txt` usually reveal why. The full file can be >1 MB for large clusters; `tail -100` rarely tells you anything useful — open from the top.
