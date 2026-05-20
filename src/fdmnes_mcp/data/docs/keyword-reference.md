---
date: 2026-05-19
project: fdmnes
type: docs-keyword-reference
---

# FDMNES — keyword reference

Comprehensive keyword catalog extracted from the parser source in `/home/nmarcella/fdmnes/fdmnes_fortran_prog/`. Cross-checked against the 97-page English manual where source comments are sparse. Companion to [docs index](2026-05-19-docs-overview.md); for usage patterns see [pipelines.md](pipelines.md).

## How keywords are matched

- Each keyword is read into a `character(len=9) :: keyword` variable in `lecture.f90:152`, so **matching is by the first 9 characters** of the input token, lowercased.
- Aliases are normalised by `Traduction()` at `main.f90:1884-2247`. Hundreds of alternative spellings collapse to a canonical name; the canonical name is what appears in the `case()` lists.
- Keywords are dispatched in `main.f90:540-656` against seven tables — `kw_all` (top-level, ~47), `kw_fdm` (FDM-mode body, ~244), `kw_conv` (convolution, ~40), `kw_metric` (~14), `kw_fit`, `kw_selec` (~5), `kw_mult` (~6), `kw_gaus` (1). Each table's keywords are written to a scratch file dedicated to its mode, then re-parsed by that mode's own subroutine.

**Totals:** ~350 distinct keywords with `case()` handlers, plus ~200 alias spellings via `Traduction()`. A handful of keywords listed in the tables (`numerov`, `bond`, `full_atom`, `delta_z_l`) have no handler body in the visible source — flagged inline below as "source unclear".

## Column legend

`Args` is the count and type of value(s) the parser consumes for the keyword. `Default` is the value before the keyword fires (from `data` statements or initial assignments). `Source ref` is the line range in the parser where you can re-find the handler.

---

## A. Top-level keywords (read in `main.f90`)

These configure the master `Fit` driver and never go to a scratch file. Source: `main.f90:662-933`.

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `bormann` | `borman` | 3 ints + 1 real (hkl, Ang_borm) | off | Sets `Bormann=.true.`; allocates 36 DAFS reflections | main.f90:847-850 |
| `check` | `icheck` | up to 30 ints | `icheck(:)=1` | Per-section verbosity (1=Lecture, 10-13=Pot0, 18=Sphere, 19=Mat/MSM, 20=Tensor, 21=Coabs, 22-25=TDDFT, 26=Hubbard, 27=SCF, 28=State, 29=Optic, 30=Convolution) | main.f90:681-693 |
| `check_all` | `checkall`, `allcheck`, `all_check` | 0 or 1 int | 3 | `icheck(:) = n` | main.f90:733-740 |
| `check_pot` / `check_sph` / `check_mat` / `check_rix` / `check_tdd` / `check_ten` / `check_coa` / `check_con` | various `_compact` aliases | 0 or 1 int | 3 | One-section verbosity | main.f90:695-719 |
| `check_mpi` | — | 0 | `.false.` | Broadcasts `icheck` across MPI ranks | main.f90:721-722 |
| `fprime_at` | `fprim_ato`, `fprimatom`, `fprimeato` | 0 or 1 int | 3 | Sets `icheck(30)`; check f' atomic table | main.f90:724-731 |
| `no_check` | — | 0 | — | `icheck(:)=0` (silences bav file) | main.f90:742-743 |
| `no_analyz` | `no_analys`, `noanalyzo`, etc. | 0 | `.true.` | Disables polarisation analyser for convolution | main.f90:745-746 |
| `circular` | `circulair` | 0 | `.false.` | Stokes circular polarisation outputs | main.f90:748-749 |
| `e_cut` | `efermi`, `ecut`, `e_cut_imp`, `e_fermi`, `ecutimp` | 1 real (eV) | -5.0 | Fermi energy `E_cut_imp` (→ Ry internally) | main.f90:751-754 |
| `epsii` | `enrgpsii`, `epsiia`, `ecore`, `e_core`, `e_psii` | 1 real (eV) | 0.0 | Reference initial-state energy `Epsii_ref` | main.f90:756-761 |
| `header` | — | 0 | `.false.` | Header lines on convolution output (for Xas Viewer / Larix) | main.f90:763-764 |
| `length_li` | — | 1 int | 10001 | `n_col_max` — column cap | main.f90:766-769 |
| `comment` | — | 1 string (132 chars) | blank | Comment string written to bav | main.f90:771-773 |
| `file_in` | `filein`, `filin` | 1 filename | — | Auxiliary input file | main.f90:775-794 |
| `filout` | `fileout`, `file_out` | 1 filename | `fdmnes_out` | **Output-file prefix** `nomfich` | main.f90:796-803 |
| `ecent` | `e_cent`, `ecenter`, `ecentre`, `e_center` | 1 real (eV) | 30.0 | Arctangent broadening centre | main.f90:805-808 |
| `elarg` | `elarge`, `e_large`, `ewidth`, `e_width` | 1 real (eV) | 30.0 | Arctangent broadening width | main.f90:810-813 |
| `estart` | `e_start` | 1 real (eV) | 100000 | Energy where convolution restarts | main.f90:815-818 |
| `gamma_hol` | — | up to 10 reals | 0 | Core-hole lifetime widths (one per edge) | main.f90:820-834 |
| `gamma_max` | — | 1 real | 10.0 | Maximum lifetime broadening width (changed 2026-03-10 from 15) | main.f90:836-840 |
| `delta_edg` | — | 1 real | 0.0 | Edge energy shift `Delta_edge` | main.f90:842-845 |
| `rixs_only` | `only_rixs` | 0 | `.false.` | Skip non-RIXS post-processing | main.f90:852-853 |
| `shift_cor` | `shift_eps`, `shift_e_c`, `core_shif` | N reals on N lines | 0 | Per-core-state energy shifts | main.f90:855-884 |
| `imfpin` | — | 1 filename | off | **FDMX**: read inelastic mean free path | main.f90:887-889 |
| `elfin` | — | 1 filename | off | **FDMX**: read ELF from file | main.f90:891-893 |
| `dwfactor` | — | 1 real | off | **FDMX**: imposed Debye-Waller | main.f90:895-897 |
| `tdebye` | — | 1 real (K) | off | **FDMX**: Debye temperature | main.f90:899-901 |
| `tmeas` | — | 1 real (K) | off | **FDMX**: measurement temperature | main.f90:903-905 |
| `expntl` | — | 2 reals | off | **FDMX**: exponential background `A·exp(-B·E)` | main.f90:907-909 |
| `victoreen` | — | 2 reals | off | **FDMX**: Victoreen background | main.f90:911-913 |
| `mermin` | — | 1 int | 0 | **FDMX**: Mermin model order | main.f90:915-916 |
| `fdmx` | — | 0 | `.false.` | Enable FDMX post-processing | main.f90:918-919 |
| `fdmx_proc` | — | 0 | `.false.` | FDMX-only run (no FDM calc) | main.f90:920-921 |
| `cm2g` | — | 0 | `.false.` | FDMX: output µ in cm²/g | main.f90:922-923 |
| `nobg` | — | 0 | `.false.` | FDMX: suppress background | main.f90:924-925 |
| `nohole` | — | 0 (also alias of `nonexc`) | `.false.` | FDMX: ground-state calc | main.f90:926-927 |
| `nodw` | — | 0 | `.false.` | FDMX: no Debye-Waller | main.f90:928-929 |
| `noimfp` | — | 0 | `.false.` | FDMX: no IMFP broadening | main.f90:930-931 |
| `test_case` | `as_before` | N ints | none | Dev/debug toggles (1=no_outer_atom, 2=test_case, 3=no XC recalc, 4=no hermitisation, 5=spin_axis_free ignored). **Dev-only.** | main.f90:664-679 |
| `end` | `fin`, `fine` | 0 | — | Terminates indata reading | main.f90:524 |
| `jump`…`endjump` | `end_jump` | block | — | Bracket-out block (comment mechanism) | main.f90:526-538 |
| `parameter` | — | block | — | Opens a Fit block; following lines list parameters | main.f90:381, 1098-1131 |

---

## B. Geometry / structure / crystallography

Source: `lecture.f90` dimension pass (`Lectdim`, lines 142-1049) plus main pass (`Lecture`, lines 2369-4500). Most-used keywords.

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `crystal` | `crist`, `cryst`, `cristallo`, `cristal` | header (3 or 6 reals) + per-atom lines | — | Periodic unit cell; `Matper=.true.` | lecture.f90:729-813, 3974-4085 |
| `crystal_t` | — | header + per-atom with thermal/occupancy fields | — | Periodic + B/U/occ columns | lecture.f90:729-813 |
| `molecule` | `molec`, `molecola` | as `crystal` (Cartesian coords) | — | Cluster (`Matper=.false.`) | lecture.f90:729 |
| `molecule_` | — | as `crystal_t` for molecule | — | Molecule with thermal fields | lecture.f90:729-813 |
| `film` | — | as `crystal` | — | 2D film (Film=.true.) | lecture.f90:729-813 |
| `film_t` | — | as `film` with U/B/occ | — | Film with thermal | lecture.f90:729-813 |
| `surface` | — | header + atoms | — | Surface layer | lecture.f90:729-813 |
| `interface` | — | header + atoms | — | Interface layer | lecture.f90:729-813 |
| `cif_file` | `cristal_c`, `crystal_c`, `ciffile` | 1 filename (`.cif` auto-appended) | — | Import structure from CIF | lecture.f90:816-955, 4188-4391 |
| `film_cif_` | — | 1 filename | — | CIF for film section | lecture.f90:816 |
| `pdb_file` | `cristal_p`, `crystal_p`, `pdbfile` | 1 filename (`.pdb` auto-appended) | — | Import structure from PDB; sets `Occupancy=.true.`, `n_temp=1` | lecture.f90:956-1019, 4088-4185 |
| `film_pdb_` | — | 1 filename | — | PDB for film | lecture.f90:956 |
| `spgroup` | — | 1 string (≤13 chars) | blank | Space group symbol (`Fd-3m:1`, `227:1`, etc.) | lecture.f90:320-324, 3967-3971 |
| `pointgrou` | `sym`, `point_gro` | 1 string | auto | Force point group; disables auto-detection | lecture.f90:3944-3962 |
| `symmol` | `sym_mol` | 0 | `.false.` | Use molecular point group | lecture.f90:3964-3965 |
| `symsite` | — | header + per-prototype site lists | — | Manually impose site equivalence | lecture.f90:3250-3273 |
| `atom` | `atome`, `atoms`, `atomes`, `atomo`, `atomi` | per-type: `Z, nlat, (n,l,pop[,popdn]) ×nlat` | — | Defines atomic types with valence config; structure block uses type number | lecture.f90:688-718, 3818-3880 |
| `atom_conf` | — | per-conf: `nb_atoms, igr(:), nlat, (n,l,pop) ×nlat` | — | Per-site config override on selected groups | lecture.f90:638-666, 3775-3816 |
| `atom_nsph` | — | hybridization orbital block | none | Non-spherical orbitals; `Atom_nonsph=.true.` | lecture.f90:668-686, 3882-3911 |
| `atom_b_is` | `temperatu` | 0 (flag) | `.false.` | Crystal block reads 1 B-iso column | lecture.f90:329, 2374-2375 |
| `atom_b_an` | — | 0 (flag) | `.false.` | Reads 3 anisotropic B columns (`n_temp=3`) | lecture.f90:326, 2377-2378 |
| `atom_u_is` | — | 0 (flag) | `.false.` | Same in U units (B = 8π²U) | lecture.f90:329, 2380-2381 |
| `atom_u_an` | — | 0 (flag) | `.false.` | Anisotropic U | lecture.f90:326, 2383-2384 |
| `occupancy` | — | 0 (flag) | `.false.` (PDB implicit) | Reads partial-occupancy column | lecture.f90:332-334 |
| `dpos` | — | 3 reals | (0,0,0) | Translation offset on all positions | lecture.f90:4392-4394 |
| `test_dist` | `testdistm`, `dist_min`, `distmin`, `distamin` | 1 real (Å) | 0.7·bohr | Min inter-atom distance threshold | lecture.f90:4396-4398 |
| `noncentre` | — | 0 | `.false.` | Don't centre cluster on absorber; `State_all=.true.` | lecture.f90:3111-3113 |
| `center` | `centre` | 0 or 3 reals | auto | Move centre to position (or `Centre_auto`) | lecture.f90:3115-3128 |
| `center_s` | — | 2 reals | — | 2D centre (x, y) only | lecture.f90:3130-3139 |
| `center_ab` | `centre_ab`, `centreabs`, `centerabs` | 0 or 3 reals | auto | Centre on absorber; `Centre_auto_abs=.true.` | lecture.f90:3141-3155 |
| `bulk` | — | header (3 or 6 reals) + `n_atom_bulk` atom lines | none | Semi-infinite substrate layer; `Bulk=.true.` | lecture.f90:153-177, 2392-2439 |
| `bulk_atom` | — | 0 | `.false.` | "bulk_atom_not_recalculated"; `Bulk_atom_used=.true.` | lecture.f90:2441-2442 |
| `bulk_roug` | — | 1 real | 0 | Bulk surface roughness | lecture.f90:2444-2446 |
| `cap_layer` | — | header + atoms | none | Capping layer above film | lecture.f90:179-189, 2448-2465 |
| `cap_b_iso` | — | 1 real | 0 | Cap B-iso | lecture.f90:2467-2469 |
| `cap_u_iso` | `cap_disor` | 1 real | 0 | Cap U-iso | lecture.f90:2471-2474 |
| `cap_rough` | — | 1 real | 0 | Cap roughness | lecture.f90:2476-2478 |
| `cap_thick` | — | 1 real | −1000 | Cap thickness | lecture.f90:2480-2482 |
| `cap_shift` | — | 1 real | −1000 | Cap z-shift | lecture.f90:2484-2486 |
| `film_roug` | — | 1 real | 0 | Film roughness | lecture.f90:2568-2570 |
| `film_shif` | — | 1-4 reals (z or x,y,z[,θ]) | (0,0,0,0) | Film translation/rotation offset | lecture.f90:2572-2580 |
| `film_zero` | — | 1 real | −1000 | Film reference z=0 plane | lecture.f90:2582-2584 |
| `film_thic` | — | 1 real | 0 | Film thickness | lecture.f90:2586-2588 |
| `surface_s` | — | 1, 3 or 4 reals | 0 | Surface layer shift | lecture.f90:2616-2626 |
| `inter_shi` | — | 1, 3 or 4 reals | 0 | Interface layer shift | lecture.f90:2604-2614 |
| `hkl_film` | `hkl_sur` | 0 | hkl=surface | hkl indices refer to film cell | lecture.f90:2593-2595 |
| `hkl_int` | — | 0 | — | hkl indices refer to interface | lecture.f90:2597-2599 |
| `doping` | — | 2 ints (itype, igr) | none | Dope atom group `igr` with type `itype` (low concentration; symmetry preserved) | lecture.f90:194-198, 2541-2543 |
| `z_absorbe` | `zabsorber`, `zabsorbeu`, `numatabs`, `numat_abs` | 1+ ints | — | Atomic number(s) of absorbers | lecture.f90:226-241, 4461-4473 |
| `absorbeur` | `iabsorbeu`, `absorbor`, `assorbito`, `absorber` | 1+ ints (atom indices) | 1 | Explicit absorber atom indices; `Absauto=.false.` | lecture.f90:209-224, 3764-3773 |
| `coop` | `coop_atom`, `atom_coop` | up to N ints | off | COOP analysis between atoms; `COOP=.true.` | lecture.f90:191-192, 2488-2491 |
| `coop_dist` | `dist_coop` | 1 or 2 reals | (0,0) | COOP pair distance window | lecture.f90:2493-2504 |
| `coop_z_ax` | `coop_z_fi`, `coop_fixe` | 0 | along-bond | Use fixed z-axis instead of along-bond | lecture.f90:2506-2507 |
| `counter_a` | — | index + 3-8 numbers | — | Counter-atom (probe) positions/charge/width/orient | lecture.f90:720-726, 2512-2536 |

## C. Energy range

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `range` | `gamme` | odd N reals: `E0, dE1, E1, dE2, ... Emax` | (-5,0.5,60); `nenerg_s=125` | Energy grid (Å, eV) | lecture.f90:372-461, 2722-2728 |
| `rangel` | `gammel` | 1 or N reals | — | Logarithmic step rule (constant-k) | lecture.f90:372-394 |
| `rixs_ener` | `energ_rix`, `energ_in_`, `ener_rixs`, `rixs_rang`, `range_rix` | N reals | — | RIXS incident-energy grid `Energ_rixs(:)` | lecture.f90:372, 2730-2762 |
| `eimag` | `potimag`, `e_imag` | rows of 1 or 2 reals | 0 | Imaginary energy `eimagent` (Green's function broadening) | lecture.f90:463-471, 3932-3942 |
| `eneg` | — | 0 | `.false.` | Allow below-Fermi calc | lecture.f90:2831-2834 |
| `not_eneg` | `noteneg` | 0 | `.false.` | Disable `eneg` | lecture.f90:2836-2837 |
| `e_out_min` | `eclie`, `delta_e_o`, `etatlie`, `delta_v_o`, `Ec_out_mi`, `Ek_out_mi`, `Ek_min`, `Ec_min` | 1 or 2 reals | (0.2, 1.0) | Binding-energy step | lecture.f90:2821-2829 |
| `ephot_min` | — | 1 real | −10⁶ | Min photon energy for output | lecture.f90:2926-2928 |
| `eloss_max` | `e_loss_ma`, `elossmax`, `e_lossmax` | 1 real | 10000 | Max energy loss for NRIXS | lecture.f90:2628-2631 |
| `energphot` | `enrgphot`, `energpho`, `ephoton` | 0 | `.false.` | Output as absolute photon energies | lecture.f90:2764-2765 |

## D. Method choice (FDM vs MS / Green)

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `green` | — | 0 | `.false.` | **Multiple scattering instead of FDM** | lecture.f90:3486-3487 |
| `green_bul` | `greenbulk`, `bulk_gree`, `bulkgreen` | 0 | `.false.` | Green's function for bulk part | lecture.f90:3489-3490 |
| `fdm_comp` | — | 0 | `.false.` | FDM with complex wavefunctions | lecture.f90:2638-2639 |
| `iord` | — | 1 int (2, 4, 6) | 4 | Finite-difference order | lecture.f90:3590-3593 |
| `adimp` | `interpoin`, `inter_poi` | 1 real or odd N reals | — | FDM grid spacing (Å); energy-dependent allowed | lecture.f90:355-370, 3595-3603 |
| `radius` | `rayon`, `rsort`, `rsorte`, `raggio` | 1 real or odd N reals | 3.0 | Cluster radius (Å); energy-dependent allowed | lecture.f90:339-353, 2930-2937 |
| `rpotmax` | — | 1 real | 0 | Max potential radius beyond `radius` | lecture.f90:2949-2952 |
| `over_rad` | `overad`, `overrad` | 1 real | 0 | Outer atom overlap radius | lecture.f90:2954-2958 |
| `overlap` | — | 1 real | 0.1 | Atomic-sphere overlap factor for MT | lecture.f90:3582-3585 |
| `muffintin` | `muffin_ti` | 0 | `.false.` | Force MT sphere potential | lecture.f90:3587-3588 |
| `lmax` | `lmaxat`, `lmaxat0`, `lmax_at`, `lmax_atom` | 1 int | −1 (auto) | Manual ℓ-max for atomic wavefunctions | lecture.f90:3610-3613 |
| `lmaxfree` | — | 0 | `.false.` | Relax ℓ-max constraint | lecture.f90:3615-3616 |
| `lmaxstden` | `lmax_doso` | 1 int | −1 | ℓ-max for DOS output | lecture.f90:3618-3621 |
| `lmaxso` | `lmaxso0`, `lmax_so`, `lmax_sor`, `lmaxsort` | 1 int | −5 | ℓ-max for spin-orbit / outer sphere | lecture.f90:3623-3626 |
| `lmaxso_ma` | — | 1 int | 28 | Hard upper limit on `lmaxso` | lecture.f90:3628-3631 |
| `lmax_pot` | — | 1 int | 1 | ℓ-max for potential expansion (with `full_pote`) | lecture.f90:2641-2649 |
| `full_pote` | — | 0 or 1 int | off | `Full_potential=.true.` | lecture.f90:2641-2649 |
| `lminus1` | `lmoins1` | 0 | `.false.` | Use ℓ−1 channel only (E1 selection rule) | lecture.f90:2844-2845 |
| `lplus1` | — | 0 | `.false.` | Use ℓ+1 channel only | lecture.f90:2847-2848 |
| `base_reel` | `basereel`, `real_basi`, `real_base` | 0 | `.true.` | Real spherical harmonics | lecture.f90:2850-2851 |
| `base_comp` | `basecomp` | 0 | — | Complex spherical harmonics | lecture.f90:2853-2854 |
| `ylm_comp` | `ylm_compl`, `ylmcomp`, `ylmcomple`, `harmo_com`, `harmocomp` | 0 | `.false.` | Force complex Ylm | lecture.f90:4400-4401 |
| `harm_tess` | `harmo_tes`, `harm_real`, `harmo_rea`, etc. | 0 | `.true.` | Disable cubic harmonics; `Harm_cubic=.false.` | lecture.f90:2590-2591 |
| `normaltau` | `normal_ta` | 0 | `.false.` | Use "normal" τ matrix variant | lecture.f90:3108-3109 |
| `solsing` | `singsol`, `solsing_o` | 0 | off | Use only singular solution | lecture.f90:3497-3499 |
| `no_solsin` | — | 0 | — | Disable singular solution | lecture.f90:3501-3502 |
| `non_relat` | `nonrelat`, `nonrelati` | 0 | 0 | Non-relativistic core wavefunctions | lecture.f90:2883-2884 |
| `relativis` | `relat` | 0 | `.false.` | Full relativistic Dirac core wavefunctions | lecture.f90:2880-2881 |
| `no_dft` | — | 0 | `.false.` | Disable DFT XC | lecture.f90:2886-2887 |
| `nrato` | `nrato_dir`, `nratodira`, `nr_ato` | 1 int | 600 | Radial points for Dirac (`nrato_dirac`) | lecture.f90:2939-2942 |
| `multrmax` | — | 1 int | 1 | Radial integration multiplier | lecture.f90:2944-2947 |
| `ray_max_d` | — | 1 real | 0 | Max Dirac radial range | lecture.f90:3507-3510 |
| `d_max_pot` | `dmaxpot`, `dmax_pot`, `d_maxpot`, `distmaxpo`, `dist_maxp` | 1 real | 2.5 | Max distance for potential calc | lecture.f90:4475-4477 |
| `numerov` | — | — | — | Listed in `kw_fdm` (main.f90:369). **Source unclear — no case() body in lecture.f90.** | — |

## E. SCF (self-consistent field)

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `scf` | `selfcons`, `self_cons` | 0-3 numbers: `nself, p_self0, Delta_En_conv` | nself=0 | Enable SCF | lecture.f90:3677-3688 |
| `n_self` | `n_scf`, `nself`, `nscf` | 1 int | 100 | Max SCF iterations | lecture.f90:3704-3706 |
| `p_self` | `p_self0`, `pself`, `pself0`, `p0_self`, `p_scf`, `p0_scf`, `pscf`, `pscf0`, `p0scf` | 1 real | 0.1 | Initial mixing fraction | lecture.f90:3696-3698 |
| `p_self_ma` | `p_scf_max`, `pselfmax`, `pscfmax`, `p_scfmax`, `p_selfmax`, `pself_max` | 1 real | 1.0 | Max mixing fraction | lecture.f90:3700-3702 |
| `r_self` | `r_selfcon`, `rself`, `rselfcons`, `r_scf`, `rscf` | 1 real | (Radius) | SCF cluster radius | lecture.f90:3711-3714 |
| `scf_exc` | `selfexc`, `self_exc`, `scfexc` | 0 | `.false.` | SCF with core hole | lecture.f90:3716-3718 |
| `scf_non_e` | `selfnonex`, `self_non_`, `self_none`, `scfnonexc`, `scf_nonex`, `scf_nohol`, `scf_no_ho` | 0 | `.false.` | SCF without core hole | lecture.f90:3720-3722 |
| `scf_abs` | — | 0 | `.false.` | SCF with charged absorber | lecture.f90:3693-3694 |
| `scf_mag_f` | — | 0 | `.false.` | Free spin polarisation during SCF | lecture.f90:2685-2686 |
| `scf_smoot` | `smouth_sc`, `smouth_se` | 0 | `.false.` | SCF smoothing | lecture.f90:3237-3238 |
| `scf_step` | `step_scf`, `pas_scf` | 1 real | — | Imposed SCF step `Pas_SCF` | lecture.f90:4479-4482 |
| `no_scf_bu` | `noscf_bul`, `no_scfbul`, `noscfbulk`, `no_self_b` | 0 | `.false.` | Skip SCF for bulk | lecture.f90:3690-3691 |
| `one_scf` | — | 0 | `.false.` | Single SCF reused for all runs | lecture.f90:4417-4418 |
| `one_scf_s` | — | 0 | `.false.` | Same for surface variant | lecture.f90:4420-4421 |
| `delta_en_` | `converge`, `deltae`, `delta_e_c`, `delta_en`, `delta_e_s` | 1 real | 0.1 × N_atoms (eV) | SCF energy convergence threshold | lecture.f90:3673-3675 |
| `nonexc` | `non_exc`, `nonexcite`, `non_excit`, `no_hole`, `nohole` | 0 | varies by edge | Ground-state (no core hole) | lecture.f90:3724-3726 |
| `excited` | — | 0 | varies by edge | Force core-hole final state | lecture.f90:3728-3729 |
| `no_fermi` | `nofermi` | 0 | — | Skip Fermi-level auto-determination | lecture.f90:3731-3732 |
| `core_ener` | `E_core_to`, `E_tot_cor`, `Etot_core`, `Ecore_tot`, `Epsii_tot` | 0 | `.false.` | Use total core energy reference | lecture.f90:2509-2510 |

## F. Potential / exchange-correlation

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `hedin` | `hedin_lun`, `hedinlund` | 0 | `.false.` | Hedin-Lundqvist LDA XC (the pre-2026-03-10 default) | lecture.f90:3636-3637 |
| `perdew` | — | 0 | `.false.` | Perdew-Wang LDA XC | lecture.f90:3639-3640 |
| `xalpha` | `xalfa`, `alfpot` | 1 real | — | Xα with given α | lecture.f90:3642-3645 |
| `pbe96` | — | listed (no body) | `.true.` | **PBEGA** GGA potential — default since 2026-03-10 (despite name, the source uses `PBE96`-tagged code with PBE/GGA functional). Note: `FDMNES_Modifications.txt` calls it PBEGA, manual still calls it PBE96. | lecture.f90:2264 |
| `clementi` | — | 0 | `.false.` | Clementi-Roetti atomic functions | lecture.f90:2682-2683 |
| `chfree` | `chlibre`, `ch_free`, `chlib`, `freech`, `free_char`, `free_ch`, `charge_fr`, `chargefre` | 0 | `.false.` | Free total charge | lecture.f90:3633-3634 |
| `v0imp` | `voimp`, `v0bdcfim`, `vmoyf`, `korigimp` | 1+ reals | — | Impose interstitial V₀ (per spin) | lecture.f90:3920-3925 |
| `vmax` | `v_intmax`, `v_max` | 1 real | 10⁶ Ry | Cap on asymptotic potential; use `Vmax -6` for molecules in solution | lecture.f90:3927-3930 |
| `rmt` | — | up to ntype reals | 0 | Per-type muffin-tin radii | lecture.f90:3605-3608 |
| `rmtg` | `rmtimp`, `rmt_imp`, `rmtgimp`, `rmtg_imp` | up to ntype reals | — | Per-type guess RMT | lecture.f90:3546-3561 |
| `rmtg_z` | `z_rmtg`, `zrmtg`, `rmtgz` | rows of `Z, R` | — | Per-element RMT table | lecture.f90:3563-3572 |
| `rmtv0` | `rmtvo` | reals (per spin) | — | RMT chosen so V(RMT)=V₀imp | lecture.f90:3574-3580 |
| `norman` | — | 0 | — | Norman criterion for RMT | lecture.f90:3504-3505 |
| `rcharge` | `rchimp` | up to ntype reals | 0 | Per-type ionic charge radii | lecture.f90:3522-3534 |
| `rcharge_z` | `rchimp_z`, `z_rcharge` | rows of `Z, R` | — | Per-element ionic radii | lecture.f90:3536-3544 |
| `rionic_z` | `rionic`, `r_ionic`, `z_rionic`, `z_r_ionic` | rows of `Z, R` | — | Per-element ionic charges | lecture.f90:3512-3520 |
| `screening` | `ecrantage` | 1, 2, 3 or 4 numbers (`n_e` alone, or `ne, le, ecr1[, ecr2]`) | 1/nspin | Imposed screening charge (1 e on first non-full valence by default); 2 numbers for spin-up/down separately | lecture.f90:1046, 2960-2975 |
| `atomic_sc` | — | 0 | `.false.` | Atomic-screening only | lecture.f90:3004-3005 |

## G. Spin / magnetism / spin-orbit

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `magnetism` | `magnetiqu`, `magnetic` | 0 | off | Sets `nspinp=2` for collinear spin-polarised | lecture.f90:537-538 |
| `spinorbit` | `spin_orbi` | 0 | off | Sets `nspinp=2, nspino=2`; spin-orbit in final state | lecture.f90:482-484, 2856-2857 |
| `spin_axis` | `axespin`, `axis_spin`, `spin_axes` | 0 | `.false.` | `Spin_axis_free=.true.` | lecture.f90:2386-2387 |
| `ang_spin` | `angspin`, `spin_ang` | up to 3 reals (deg) | (0,0,0) | Spin axis Euler angles | lecture.f90:2865-2870 |
| `axe_spin` | (overlap with `axespin`) | 3 reals | — | Spin axis vector (in direct-lattice basis) | lecture.f90:2872-2875 |
| `mag_axis_` | — | 0 | `.false.` | Mag axis free (`Mag_axis_free=.true.`) — disables grid rotation with spin axis | lecture.f90:2676-2677 |
| `z_nospino` | — | 1 int | 0 | Atomic number to suppress spin-orbit on | lecture.f90:2903-2906 |
| `e_moment` | `elec_mome`, `electric_`, `elec_fiel`, `e_field` | 3 or 4 reals | (0,0,0) | Electric-moment / Stark axis vector | lecture.f90:2545-2560 |

## H. Multipoles / transitions

Default: `E1E1=.true.` only (lecture.f90:2122). Umbrella keywords (`Quadrupole`, `Octupole`, `Dipmag`, `Quadmag`, `Dip_rel`) enable channel groups; granular `EXXX` keywords enable single channels; `No_EXXX` disable.

| Keyword | Aliases | Args | Effect | Source ref |
|---|---|---|---|---|
| `e1e1` | `dipole` | 0 | Electric dipole (default) | lecture.f90:3032-3033 |
| `e1e2` | — | 0 | Dipole-quadrupole interference | lecture.f90:3035-3037 |
| `e1e3` | `e3e1` | 0 | Dipole-octupole | lecture.f90:3039-3040 |
| `e2e2` | — | 0 | Quadrupole-quadrupole | lecture.f90:3051-3052 |
| `e3e3` | — | 0 | Octupole-octupole | lecture.f90:3057-3058 |
| `e1m1` | — | 0 | E-mag dipole interference | lecture.f90:3042-3043 |
| `e1m2` | — | 0 | E1-M2 interference | lecture.f90:3045-3046 |
| `m1m1` | `m1_m1` | 0 | Magnetic dipole | lecture.f90:3060-3061 |
| `m1m2` | `m1_m2`, `m2m1`, `m2_m1` | 0 | M1-M2 interference | main.f90:365 |
| `m2m2` | — | 0 | M2-M2 | lecture.f90:3063-3064 |
| `e2m2` | — | 0 | E2-M2 | lecture.f90:3054-3055 |
| `e1sp` | — | 0 | E1-Spin (relativistic) | lecture.f90:3048-3049 |
| `spsp` | — | 0 | Spin-spin | lecture.f90:3066-3067 |
| `quadrupol` | `quadripol` | 0 | Umbrella: enable E2 channel | lecture.f90:473-474, 3026-3027 |
| `octupole` | `dipole_oc`, `dip_oct` | 0 | Umbrella: enable E3 channel | lecture.f90:3029-3030 |
| `dipmag` | `magdip`, `dip_mag`, `mag_dip` | 0 | Umbrella: E1M1 + M1M1 | lecture.f90:3069-3072 |
| `quadmag` | `magquad`, `dip_quad` | 0 | Umbrella: E1M2 + E2M2 + M1M2 + M2M2 | lecture.f90:3074-3079 |
| `dip_rel` | `dip_relat`, `spin_pos`, `spin_posi` | 0 | Umbrella: E1SP + SPSP (spin-position) | lecture.f90:2633-2636 |
| `no_e1e1` | `notdipole`, `nondipole`, `nodipole`, `no_dipole`, `noe1e1` | 0 | Turn off default E1E1 | lecture.f90:3081-3082 |
| `no_e1e2` | `no_dipqua`, `nodipquad`, `nondipqua`, `noe1e2` | 0 | Disable E1E2 | lecture.f90:3090-3091 |
| `no_e1e3` | `noe1e3`, `noe3e1`, `no_e3e1` | 0 | Disable E1E3 | lecture.f90:3087-3088 |
| `no_e2e2` | `noe2e2` | 0 | Disable E2E2 | lecture.f90:3084-3085 |
| `no_e3e3` | — | 0 | Disable E3E3 | lecture.f90:3093-3094 |
| `no_res_ma` | — | 1 real | 1.0 | Non-resonant magnetic factor `f_no_res(1)` | lecture.f90:2895-2897 |
| `no_res_mo` | — | 1 real | −100 (Hund × 0.2) | Non-resonant moment factor `f_no_res(2)` | lecture.f90:2899-2901 |
| `ldipimp` | — | 3 ints | (−1,−1,−1) | Impose ℓ values for dipole channel | lecture.f90:3096-3099 |
| `lquaimp` | `lquadimp` | 3×3 ints | (−1,−1,−1) | Impose ℓ values for quadrupole | lecture.f90:3101-3106 |
| `all_trans` | — | 0 or 1 int (1-4) | 1 / 4 | Number of transition multipoles combined | lecture.f90:3193-3202 |
| `all_nrixs` | `allnrixs`, `allnrix`, `allxraman`, `all_xrama` | 0 | `.false.` | All-multipole NRIXS | lecture.f90:3190-3191 |
| `lmax_nrix` | `lmaxnrixs`, `lmax_xram`, `lmaxxrama` | 1 int | 2 | ℓ-max for NRIXS expansion | lecture.f90:249-250, 3204-3205 |
| `edge` | `seuil`, `threshold`, `soglia` | 1 string | `K1` | Edge to compute (`K`, `K1`, `L1`-`L3`, `L23`, `M1`-`M5`, `M23`, `M45`, `N1`-`N5`, `N23`, `N45`, `O1`-`O5`) | lecture.f90:3007-3024 |

## I. Spectroscopy modes

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `optic` | `optics`, `optique` | 0 | `.false.` | Optical-spectra mode | lecture.f90:2679-2680 |
| `xan_atom` | — | 0 | `.false.` | Per-atom XANES contributions | lecture.f90:336-337 |
| `tddft` | `xcorr`, `tdlda`, `td_lda`, `td_dft` | 0 | `.false.` | TDDFT post-processing | lecture.f90:2977-2978 |
| `rpalf` | `rpa`, `rpa_lf` | 0 | `.false.` | RPA with local field; auto-enables `tddft` | lecture.f90:2980-2982 |
| `dyn_eg` | — | 0 | `.false.` | TDDFT diagonal-kernel on edges; auto-`tddft` | lecture.f90:2984-2986 |
| `dyn_g` | `dynamical` | 0 | `.false.` | TDDFT diagonal-kernel on initial states; auto-`tddft` | lecture.f90:2988-2990 |
| `kern_fac` | — | 1 real | default | TDDFT kernel scaling | lecture.f90:2992-2996 |
| `kern_fast` | — | 0 | `.false.` | Fast TDDFT kernel | lecture.f90:2998-2999 |
| `gamma_tdd` | — | 0 | `.false.` | Lifetime broadening in TDDFT | lecture.f90:3001-3002 |
| `lmax_tddf` | — | 1 int | -1 (auto: 2/3) | TDDFT ℓ-max | lecture.f90:3207-3208 |
| `rixs` | — | optional emission line + rows of 3-4 reals | off | `RIXS=.true.`; list of q-vectors | lecture.f90:252-296, 4443-4456 |
| `full_xane` | — | as `rixs` | off | Same path (full XANES + emission alias) | lecture.f90:252 |
| `nrixs` | `nixs`, `xraman`, `xramman`, `ramanx`, `rammanx` | rows of q magnitudes | — | NRIXS / X-Raman | lecture.f90:298-318, 3210-3217 |
| `nrixs_mon` | — | rows of 4 reals (`|q|, qx, qy, qz`) | — | Monocrystal NRIXS | lecture.f90:298, 3219-3235 |
| `density` | `state_den`, `statedens`, `densite` | 0 | `.false.` | DOS / density output | lecture.f90:2767-2768 |
| `density_c` | — | 0 | — | Density + complex output | lecture.f90:2770-2772 |
| `density_s` | — | 0 | — | Density + spin-projected | lecture.f90:2774-2776 |
| `density_a` | `stateall`, `state_all`, `densityal` | 0 | — | Density at all sites | lecture.f90:2778-2781 |
| `allsite` | `all_site` | 0 | `.false.` | Output spectra at every absorbing site | lecture.f90:3187-3188 |
| `extract` | `extractio` | 1 filename | — | Re-extract from prior bav file | lecture.f90:200-207, 2700-2705 |
| `extract_t` | — | as `extract` | — | Tensor-terms extraction variant | lecture.f90:2700 |
| `polarized` | `polarise`, `polarised`, `polarisat`, `polarizat`, `polar`, `polarize` | rows of 3, 4, 6, 7 or 8 reals | nple=0 | Polarisation vectors (optional wave vector / weights) | lecture.f90:548-558, 3157-3180 |
| `mat_polar` | — | rows of 6 reals | — | Polarisation matrix (non-resonant) | lecture.f90:560-567, 3182-3185 |
| `dafs` | `dafsscan`, `dafscan`, `rxs`, `rxd` | rows of 3,5,6,7,8 numbers | — | Resonant diffraction reflections | lecture.f90:569-604, 3275-3391 |
| `dafs_2d` | `rxs_2d`, `rxd_2d`, `dafs_surf`, `rxs_surfa`, `rxd_surfa` | rows of 10-13 numbers | — | 2D-DAFS with surface diffractometer | lecture.f90:569, 3397-3456 |
| `dafs_exp` | `rxs_bio`, `rxd_bio`, `rxsbio`, `rxdbio`, `dafsbio`, `rxs_exp`, `rxd_exp` | orientation matrix + per-file (angle, filename) | — | DAFS from experimental data files | lecture.f90:606-627, 3458-3484 |
| `self_abs` | `selfabsor`, `self_abso`, `selfabs` | 0 | `.false.` | DAFS self-absorption correction | lecture.f90:632-633 |
| `full_self` | — | 0 | `.false.` | Full self-absorption (×4 µ columns; birefringence) | lecture.f90:635-636 |
| `setaz` | — | 3 ints | (0,0,1) | Reference reflection `hkl_ref` for azimuth zero | lecture.f90:4458-4459 |
| `zero_azim` | — | 3 reals | (0,0,1) | Azimuthal origin vector | lecture.f90:3492-3495 |
| `step_azim` | `stepazim`, `stepazimu`, `azim_step` | 1 real (deg) | 2 | `nphim = 360 / |step|` | lecture.f90:3240-3248 |
| `phi_0` | — | 1 real | 0 | Reference azimuthal angle | lecture.f90:3393-3395 |
| `mat_ub` | — | 9 reals (3×3) | 0 | UB orientation matrix for surface DAFS | lecture.f90:4423-4438 |
| `theta_in` | `theta_i`, `teta_i`, `teta_in`, `theta-i`, `theta-in`, `teta-i`, `teta-in` | 1 or 3 reals | — | Incidence θ | lecture.f90:516-535, 2796-2804 |
| `two_theta` | `2_theta`, `2_teta`, `two_teta`, `two-theta`, `two-teta`, `2theta`, `2teta`, `twotheta`, `twoteta` | 1 or 3 reals | — | 2θ | lecture.f90:486-505, 2786-2794 |
| `theta_2th` | `theta_two` | rows of 1 or 2 reals | — | (θ, 2θ) pairs for RIXS scans | lecture.f90:507-514, 2806-2816 |
| `powder` | — | 0 | `.false.` | Powder-average | lecture.f90:2818-2819 |
| `delta_g_r` | `delta_gau` | 1 real | 0 | Gaussian width for RIXS (`Delta_Gauss_rixs`) | lecture.f90:2538-2539 |
| `moment_co` | — | 0 | `.false.` | Moment conservation for RIXS | lecture.f90:4440-4441 |
| `cartesian` | `cartesien` | 0 | `.false.` | Output tensors in Cartesian basis | lecture.f90:2697-2698 |
| `spherical` | — | 0 | `.false.` | Spherical-tensor output | lecture.f90:2690-2691 |
| `sphere_al` | `sphere_si` | 0 | `.false.` | Signal in spherical basis | lecture.f90:2693-2695 |
| `Only_indi` | — | 0 | `.false.` | Only indirect RIXS terms | lecture.f90:2707-2708 |
| `epsif` | — | 1 real | 0 | Reference energy in final state | lecture.f90:2562-2566 |
| `supermuf` | — | 0 | `.false.` | Super muffin-tin | lecture.f90:2783-2784 |
| `rydberg` | — | 0 or 1 real | R_rydb=1 | Rydberg radius factor | lecture.f90:2839-2842 |
| `core_reso` | `spinresol`, `coreresol` | 0 | `.false.` | Core-resolved output (j-split) | lecture.f90:2859-2860 |
| `no_core_r` | various | 0 | `.false.` | Disable core resolution | lecture.f90:2862-2863 |
| `debye` | — | 1 real (K) | 0 | Debye temperature (validated 0≤T<10000) | lecture.f90:2908-2924 |

## J. Hubbard / strongly correlated

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `hubbard` | `hubard` | up to ntype reals (U-J in eV) | 0 | Per-atom-type Hubbard U; nonzero → `Hubb(it)=.true.` | lecture.f90:246-247, 3734-3749 |
| `hubbard_z` | — | rows of `Z, V` | — | Per-element Hubbard table | lecture.f90:246, 3751-3759 |
| `full_atom` | — | — | `.true.` | Default-on in 2026-03-10 (Full_atom_e=.true.). **Source unclear** — no case() body; only `spgr_atom` flips it off. | lecture.f90:2151 |
| `spgr_atom` | — | 0 | — | `Full_atom_e=.false.` — restore pre-2026 space-group equivalence | lecture.f90:3761-3762 |

## K. FLAPW / Wien2k import

Source: `lecture.f90:1020-1041, 3647-3671`. Each variant takes a set of filenames.

| Keyword | Args | Effect |
|---|---|---|
| `flapw` (`lapw`, `wien`) | 5 filenames | Basic FLAPW potential import |
| `flapw_s` (`lapw_s`, `wien_s`) | + save filename | Save potential to file |
| `flapw_r` (`lapw_r`, `wien_r`) | + saved filename | Reload from saved potential |
| `flapw_s_p` | filenames | Save + paste mode |
| `flapw_psi` | filenames | Include FLAPW wavefunctions |
| `flapw_n` | filenames | New FLAPW format; `Flapw_new=.true.` |
| `flapw_n_p` | filenames | New format + ψ |
| `flapw_s_n` | filenames | Save + new |

## L. Helmholtz layer / electrochemistry

| Keyword | Aliases | Args | Effect | Source ref |
|---|---|---|---|---|
| `helmholtz` | `helm`, `helmoltz`, `helmhotz`, `helmotz`, `helmolz` | 2 or 3 reals (`V, Δ[, width]`) | Helmholtz double-layer potential | lecture.f90:2651-2674 |
| `helm_cos` | — | as `helmholtz` | Cosine-shaped variant | lecture.f90:2651 |
| `helm_mix` | — | as `helmholtz` | Mixed form | lecture.f90:2651 |
| `charge_im` | `image_cha`, `image_pot` | 0 | Image-charge contribution | lecture.f90:2601-2602 |

## M. Multi-run / extraction

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `one_run` | — | 0 | `.false.` | Single run for all absorbers | lecture.f90:4407-4409 |
| `one_run_s` | — | 0 or 1 real | `Delta_plane_max=0.3` | One-run with surface | lecture.f90:4411-4415 |
| `python` | — | 0 | `.false.` | Underscore-friendly output headers | lecture.f90:2877-2878 |
| `delta_eps` | — | 1 real | 10⁶ | Epsii grouping tolerance | lecture.f90:4403-4405 |

## N. Numerical tuning / debug

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `no_ata` | — | 0 | `.false.` | Skip Average-T-Matrix for partial occupancies | lecture.f90:2371-2372 |
| `no_renorm` | — | 0 | `.false.` | `No_renorm=.true.` | lecture.f90:2889-2890 |
| `renorm` | — | 0 | `.false.` | `Renorm=.true.` | lecture.f90:2892-2893 |
| `no_cluste` | — | 0 | `.false.` | `No_cluster_rotation=.true.` | lecture.f90:3708-3709 |
| `memory_sa` | `biologie`, `biology`, `save_memo`, `savememor`, `memorysav` | 0 | `.false.` | **Minimise memory** (slower but fits big clusters) | lecture.f90:1043-1044 |
| `readfast` | `read_fast` | 0 | `.false.` | Fast input reading (less validation) | lecture.f90:629-630 |
| `dilatorb` | `dilat`, `dilatati`, `dilat_or` | rows of `itype, ℓ, factor` | — | Orbital radial dilation per type/ℓ | lecture.f90:540-546, 3913-3918 |
| `trace` | — | 1 int + optionally 3 reals | — | Trace-plane definition; aliases `trace_for/trace_wie` set `Trace_format_wien=.true.` | lecture.f90:2710-2720 |
| `bond` | — | — | — | Listed in `kw_fdm` (main.f90:350). **Source unclear** — no body. |
| `delta_z_l` | — | — | — | Listed in `kw_fdm` (main.f90:355). **Source unclear** — no body. |

## O. Convolution mode (`convolution.f90`)

Activated when any `kw_conv` keyword appears. Defaults from `main.f90:417-451`.

| Keyword | Aliases | Args | Default | Effect | Source ref |
|---|---|---|---|---|---|
| `calculati` | — | filename(s) [+ pds, shift, EF per line] | — | List of FDMNES output files to convolve | conv:1803-1885, 2017-2061 |
| `cal_tddft` | — | filename(s) | — | Same for TDDFT-output files | conv:2063-2085 |
| `convoluti` | `arc` | 0-5 reals: `Ecent, Elarg, Gamma_max, Gamma_hole, E_cut` | (30, 30, 10, 0, −5) eV | Arctangent Lorentzian | conv:2223-2261 |
| `table` | — | optional `E_cut` + rows of `E, β` | — | Custom lifetime-broadening table | conv:1887-1897, 2263-2277 |
| `seah` | `seah_denc` | 0-4 reals: `asea[, Gamma_max[, Gamma_hole[, E_cut]]]` | — | Seah-Dench inelastic broadening | conv:2194-2221 |
| `gaussian` | `resolutio`, `gaus`, `gauss` | 0, 1 or 2 reals | — | Gaussian post-broadening (FWHM) | conv:2104-2111 |
| `e_step_co` | — | 0 or 1 real | — | Output energy step `E_step_conv` | conv:2098-2102 |
| `eintmax` | — | 1 real | — | Max convolution integration energy | conv:2279-2283 |
| `gamma_fix` | — | 0 | `.true.` | Fixed-Γ (no energy dependence) | conv:2285-2286 |
| `gamma_var` | — | 0 | `.false.` | Energy-dependent Γ | conv:2288-2289 |
| `s0_2` | `s02`, `so2`, `so_2` | 1 real | — | S₀² amplitude factor (~0.8 typical) | conv:2320-2321 |
| `dec` | — | 0 | `.false.` | Pre-shift before convolution | conv:2292-2294 |
| `no_extrap` | `noextrap` | 0 | (auto-on if jseuil≥4) | Disable energy extrapolation | conv:2296-2298 |
| `nxan_lib` | — | 0 | `.false.` | Library XANES output | conv:2300-2302 |
| `per_atom` | — | 0 | `.false.` | Cross-section per absorber (Mbarn/atom) | conv:2304-2306 |
| `xes` (`photoemis`, `photo`) | — | 0 | `.false.` | Emission spectrum mode | conv:2323-2324 |
| `selec_cor` | `select_co`, `selectcor`, `seleccore`, `sel_core`, `selcore` | N ints | — | Select core states for output | conv:2326-2329 |
| `forbidden` | — | 0 | `.false.` | Output forbidden reflections | conv:2117-2119 |
| `fprime` | `fprim` | 0 | `.false.` | Output Re/Im of scattering amplitude (f', f'') | conv:2113-2115 |
| `thomson` | — | rows of `fr, fi` (×npldafs) | — | Thomson scattering correction | conv:1908-1910, 2308-2313 |
| `transpose` | — | N reals | — | Transposed RIXS / DAFS-rod output | conv:1912-1913, 2315-2318 |
| `surface_p` | — | 3 ints | — | Surface plane indices `hkl_S` | conv:2331-2334 |
| `sample_th` | — | 1 real | — | Sample thickness | conv:2336-2338 |
| `dead_laye` | — | 1 real (µm) | — | Dead layer thickness | conv:2368-2372 |
| `double_co` | — | 0 | `.false.` | Double self-absorption correction | conv:2374-2375 |
| `weight_co` | — | (n) + coupled rows | — | DAFS coupling weights | conv:1915-1926, 2377-2393 |
| `stokes` (`stoke`) | — | rows of 1-5 reals | — | Stokes-parameter analyser definitions | conv:1899-1906, 2340-2351 |
| `stokes_na` | `stokesnam`, `stokename`, `stoke_nam` | N strings | — | Names for Stokes channels | conv:2353-2366 |
| `scan` | — | 0 | `.false.` | DAFS scan format | conv:2156-2158 |
| `scan_file` | — | filenames (×nfich) | — | Per-file DAFS scan data | conv:2121-2154 |
| `scan_conv` | `scan_out`, `scanout`, `scanconv` | 1 filename | — | Output filename for scan | conv:2160-2164 |
| `conv_out` | — | 1 filename | — | Convolution output filename | conv:2087-2091 |
| `directory` | — | 1 path | — | Prefix path for FDMNES files | conv:2166-2170 |
| `abs_b_iso` | — | 1 or 2 reals | — | Absorber B-iso (and optional shift) | conv:2172-2180 |
| `abs_u_iso` | — | 1 or 2 reals | — | Absorber U-iso | conv:2182-2189 |
| `abs_befor` | — | 0 | `.false.` | Add lower-edge background of all elements | conv:2008-2009 |
| `amplphase` | `ampl_phas`, `phase_ampl`, `phaseampl`, `phase` | 0 | `.false.` | Output amplitude + phase | conv:2014-2015 |
| `all_conv` | `conv_all` | 0 | (Just_total) | Output every per-site convolution separately | conv:2011-2012 |
| `dafs_exp_` | — | 1 int | — | DAFS experiment file format type | conv:2093-2096 |
| `check_bir` | — | 0 | `.false.` | Output birefringence check | conv:2191-2192 |
| `run_done` | — | 0 / marker | — | Marks previously-completed run | conv:2005-2006 |

## P. Metric (experimental comparison)

Triggered when any `kw_metric` keyword appears. Source: `metric.f90:88-280`.

| Keyword | Aliases | Args | Effect | Source ref |
|---|---|---|---|---|
| `experimen` | — | per-file: filename + 1-4 numbers (column indices + weights) | List of experimental files | metric.f90:100-134 |
| `file_met` | — | 1 or 2 filenames | Metric output file | metric.f90:136-179 |
| `gen_shift` | — | `e1 e2 n_shift` | Energy-shift scan range for fit metric | metric.f90:181-185 |
| `emin` | — | 1 real or N reals | Metric integration lower limit | metric.f90:187-198 |
| `emax` | — | 1 real or N reals | Metric integration upper limit | metric.f90:200-211 |
| `error` | — | 0 | Include error column | metric.f90:213-214 |
| `kev` | — | 0 | Treat energies as keV | metric.f90:217-218 |
| `rx` | `fit_rx` | 0 | Use Rx (Zanazzi-Jona) metric | metric.f90:221-222 |
| `rxg` | — | rows of spectrum indices | Group spectra for Rxg metric | metric.f90:225-265 |
| `d2` | — | 0 | D² metric | metric.f90:269-270 |
| `detail` | — | 0 | Detailed output | metric.f90:272-273 |
| `fit_out` / `metric_ou` | — | 1 filename | Fitted-parameter output | metric.f90:276-285 |
| `weight_co` | — | (parsed as in convolution) | Weight per spectrum | (kw_metric) |

## Q. Fit (parameter sweeps)

Source: `main.f90:381, 1098-1135`. Allowed parameter names in `param_conv` (main.f90:393-399).

`Parameter` opens a fit-parameter block. Each subsequent line: parameter name + 1, 2 or 3+ numbers, in one of the forms:
- `<name> <value>` — fixed at value
- `<name> <min> <max> <n_step>` — scan grid
- `<name> <min> <max> <step> <indice>` — scan grid with explicit step and block-correlation index

Parameter names accepted (from `param_conv`, with handlers in `lecture.f90:4709-4779`, `convolution.f90:323-364`, `metric.f90`):

| Parameter | What it varies |
|---|---|
| `ecent`, `elarg`, `e_cut`, `gamma_hol`, `gamma_max`, `gaussian`, `abs_u_iso`, `aseah`, `bseah` | Convolution parameters |
| `shift`, `weight`, `weight_co` | Per-spectrum / per-file values |
| `a`, `b`, `c`, `abc` | Cell parameters |
| `anga`, `angb`, `angc` | Cell angles |
| `dposx`, `dposy`, `dposz`, `posx`, `posy`, `posz` | Atom positions |
| `theta`, `phi` | Polar angles |
| `poporb` (alias `pop_orb`) | Orbital populations |
| `occup` | Occupancies |
| `v_helm`, `delta_hel`, `width_hel` | Helmholtz layer |
| `cdip_m`, `cdip_w`, `cdip_x`, `cdip_y`, `cdip_z`, `cion_ch`, `cion_w`, `cion_x`, `cion_y`, `cion_z`, `cato_x`, `cato_y`, `cato_z`, `cato_w`, `cato_ch`, `cato_o` | Counter-atom positions/charge/width |

**Rule:** parameters listed under the *same* `Parameter` block are correlated (moved together via the trailing `indice`); different blocks scan independently — the grid grows multiplicatively. Use `Metric_out` to dump the full scan metric grid.

## R. Selection (DAFS scan filtering)

Triggered by any `kw_selec` keyword. Source: `selec.f90:44-140`.

| Keyword | Aliases | Args | Effect | Source ref |
|---|---|---|---|---|
| `selec_inp` | `select_in`, `selec_in`, `selecin`, `selecinp`, `selec_ind` | 1 filename | Input scan file | selec.f90:49-54 |
| `selec_out` | `select_ou`, `selecout`, `selec_ou` | 1 filename | Output filename | selec.f90:56-61 |
| `energy` | — | N reals | List of energies to extract | selec.f90:63-85 |
| `reflectio` | `reflexion` | N ints | List of reflection indices | selec.f90:87-110 |
| `azimuth` | — | N reals (or none = full scan) | List of azimuth angles | selec.f90:112-137 |

## S. Unit-cell utility (`kw_mult`)

Source unclear — the `mult_cell` subroutine called at `main.f90:1262` is not in the visible Fortran tree. The keyword table at `main.f90:390` lists:

| Keyword | Effect (per manual § G) |
|---|---|
| `atomic_nu` | Assign atomic numbers per type |
| `cub_hexa` | Cubic ↔ hexagonal lattice transform |
| `mat_mul` | Multiplication matrix |
| `mult_cell` | Multiply unit cell (`Mult_cell 2 2 1` doubles a and b) |
| `unit_cell` | Unit-cell mode header |
| `surf_cell` | Surface-cell variant |

Until the subroutine surfaces, the **manual is the authoritative reference** for this family. Example: `Mult_inp.txt` in the test bank uses these.

## T. Gaussian-only post-processing

`Conv_gaus` (table `kw_gaus`) triggers `Gaus_cal` mode — standalone Gaussian convolution. Source: `main.f90:383, 635-647`.

---

## Gotchas, exclusivities, deprecated items

1. **9-character truncation collisions**: keywords sharing a 9-char prefix are indistinguishable to the parser. Known collisions: `Crystal_t` (thermal) vs `Crystal_c` (CIF redirect); `Trace_for` and `Trace_wie` both match `trace` and set `Trace_format_wien=.true.`. If you spell something exotic, confirm the canonical name above.

2. **`Crystal` / `Molecule` / `Film` / `Surface` / `Interface` are mutually exclusive** as the primary absorbing structure. `Bulk` / `Cap_layer` / `Surface` / `Interface` can be *added* to a `Film` to extend it.

3. **`Cif_file` / `Pdb_file` / `Flapw*`** are alternative ways to provide structure — combining with explicit `Crystal` / `Molecule` is illegal.

4. **Multipole defaults**: `E1E1=.true.` by default; the `E1E2` / `E2E2` / `E3E3` / `M1M1` keywords are *enables*. `Quadrupole` is an umbrella that turns on the *channel* (sets `Quadrupole=.true.`) — it does NOT by itself enable `E2E2`; verify via the source if a subtle channel difference matters.

5. **`Spinorbit` implies `nspinp=2, nspino=2`** — supersedes `Magnetism` which only sets `nspinp=2`. With both: spin-orbit takes precedence.

6. **Odd-count rule for `Range`, `Adimp`, `Radius`**: even-count argument lists are hard-rejected (lecture.f90:341, 358, 378). Single-value forms are fine; energy-dependent forms need odd count.

7. **Dimension-pass-only keywords**: `xan_atom`, `magnetism`, `occupancy`, `full_self`, `memory_sa`, `self_abs`, `readfast` are handled in `Lectdim` only and skipped in the main pass at `lecture.f90:4485` — repeating them in a "later" position has no extra effect.

8. **`extract` vs computing from scratch**: when `Extract` is set, most FDM internals are skipped; many keywords are silently ignored (lecture.f90:1062-1066). Useful but error-prone — verify what came through by looking at the new bav file.

9. **`numerov`, `bond`, `full_atom`, `delta_z_l`** in `kw_fdm` (main.f90:350-369) have no `case()` body in `lecture.f90`. Either dead code, placeholders, or handled in another module. **Source unclear — flag inline.**

10. **`mult_cell` family** routes to a `mult_cell` subroutine not in the visible source. Defer to manual § G.

11. **`test_case` is dev-only**: comments in `main.f90:664-679` mark these as in-source debug paths. Don't use in production input files.

12. **`check_*` family**: pure verbosity / logging. `check_all 3` is the canonical "max verbose" knob; rarely needed unless debugging.

13. **FDMX block (`fdmx`, `fdmx_proc`, `cm2g`, `nobg`, `nohole`, `nodw`, `noimfp`, `dwfactor`, `tdebye`, `tmeas`, `expntl`, `victoreen`, `mermin`, `imfpin`, `elfin`)** is contributed work (`*** JDB` markers). With `fdmx_proc` the FDM calc is skipped entirely.

14. **`nohole` is overloaded**: as a top-level `kw_all` keyword (main.f90:339, 926-927) it sets FDMX `nohole=.true.`; as an alias of `nonexc` it goes through `Traduction()`. Order matters — kw_all match happens before alias translation.

15. **`e_cut` / `efermi` are triple-handled**: top-level `kw_all` (main.f90:751) + as a fit parameter name + as a convolution-mode keyword. The first match wins.

16. **`rixs` and `full_xane`** are dimension-pass aliases (`lecture.f90:252`), but only `rixs` triggers full RIXS in the main pass (4443). `full_xane` triggers HERFD if an emission line follows.

17. **Hidden / undocumented dev flags spotted in source**: `bsc_scf` (lecture.f90:2389), `harm_tess`, `no_dft`, `python`, `moment_co`, `delta_eps`, `test_dist`, `mermin`. Use only with knowledge.

18. **`Hubbard` vs `Hubbard_z`**: both turn on Hubbard but the data layout differs. `Hubbard <vals>` is in the order of the `Atom` table (per-type); `Hubbard_z` takes `Z V` rows (per-element).

19. **`E_adimp` / `E_radius` allocation**: energy-dependent `radius` / `adimp` forms need an odd count and compute `n_range` at `lecture.f90:1140-1168`. Both can coexist.

20. **`Occupancy_first` ordering**: when both occupancy and thermal columns are in `crystal_t`, the column order depends on which keyword appeared first in the input. Parser tracks via the `Occupancy_first` flag (lecture.f90:334).

## Source file map

| Parser source | Lines | What it does |
|---|---|---|
| `main.f90` | 540-656 | Keyword dispatch by table (kw_all, kw_fdm, kw_conv, …) |
| `main.f90` | 662-933 | Top-level keyword handlers (kw_all) |
| `main.f90` | 1884-2247 | `Traduction()` alias map |
| `lecture.f90` | 142-1049 | Dimension pass (`Lectdim`) |
| `lecture.f90` | 2369-4500 | Main pass (`Lecture`) |
| `convolution.f90` | 1939-2403 | Convolution-mode parser |
| `convolution.f90` | 323-364 | Fit-parameter dispatch (convolution side) |
| `metric.f90` | 88-280 | Metric / experimental-comparison parser |
| `selec.f90` | 44-140 | Selection parser (DAFS extraction) |

## Summary statistics

- `kw_all` (top-level): 47 keywords with case() handlers
- `kw_fdm` (FDM mode): 244 declared, ~210 with visible case() bodies
- `kw_conv` (convolution): 40
- `kw_metric`: 14
- `kw_fit`: 1 (`parameter` opens block)
- `kw_selec`: 5
- `kw_mult`: 6 (source unclear)
- `kw_gaus`: 1
- Plus 41 fit-parameter names in `param_conv`
- Plus ~200 alias spellings via `Traduction()`

**Total recognised tokens: ~350 distinct keywords + ~200 aliases.**

When in doubt about whether a keyword exists: grep the parser source. The canonical pattern is `case(keyword)` in `lecture.f90` / `main.f90` / `convolution.f90`.
