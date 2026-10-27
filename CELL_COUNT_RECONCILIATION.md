# Cell Count Reconciliation: harvester `normal_cell_count` vs summary `filtered_cell_count`

_Generated 2026-08-03, revised 2026-10-27 against `sync/upstream-2026-oct-27-neocortex-retina`
(neocortex and retina data mirrored from `upstream/main` at `fb459b3a`). Regenerate with
`python3 tools/reconcile_cell_counts.py` from the repository root; results land in
`cell_count_reconciliation.csv`._

## Question

Every analyzed dataset has two independent cell counts:

- **`normal_cell_count`** — from `data/prod/<organ>/cellxgene-harvester/*.csv`. What the harvester
  expected to find: cells in the queried tissue with `disease == normal`.
- **`filtered_cell_count`** — from `master_dataset_summary_*.csv` in each results folder. What the
  NSForest run actually analyzed.

They should agree. This documents how far they actually do, across every organ and dataset.

## Method

Join on `dataset_version_id`, scoped to the same organ — the same dataset is harvested separately
per tissue, so `dataset_version_id` alone is not unique (21 IDs appear under more than one organ,
with legitimately different normal counts — 46 IDs now, up from 21 before PR #265 added the
neocortex and retina v2 harvesters).

One caveat shapes the join: **`normal_cell_count = 0` is a placeholder, not a measurement.** 269
harvester rows carry it, all in the `*_with_normal_counts.csv` files (91 respiratory system, 70
neocortex, 48 digestive tract, 31 liver, 13 bone marrow, 11 skin, 3 pancreas, 2 heart). Where one collides with an
analyzed dataset — 8 cases — the matching `*_final.csv` row carries the real number. The script
therefore prefers the largest non-zero value and records every candidate in
`harvester_normal_values` so the choice stays auditable. A naive join that takes the
`_with_normal_counts` value reports a spurious 100% shortfall on those 8.

## Result

85 summary rows across 85 `master_dataset_summary` files; 84 join to a harvester row in the same
organ. (The count was 89 rows before the 2026-10-26 sync: the recovered neocortex summary had five
rows, the new run has one.)

| Comparison | Rows |
|---|---|
| `filtered_cell_count` **==** `normal_cell_count` | 54 |
| short by 1–29 cells (median 6.5, worst 99.03% of normal) | 28 |
| **exceeds** `normal_cell_count` | 2 |
| no harvester row to join against | 1 |

The two sources agree exactly about two-thirds of the time. Where they disagree, the gap is almost
always a handful of cells. Two datasets overshoot, described below, and one (neocortex) cannot be checked at all.

### The pipeline side is internally consistent

Before comparing across sources, the results files agree with each other perfectly:

- `filtered_cell_count` == `summary_normal.n_obs` — **84/85**
- `filtered_cell_count` == sum of post-filter cluster sizes — **84/85**

The one exception is the neocortex Jorstad run: `filtered_cell_count` is 1,155,822, while
`summary_normal.n_obs` and the sum of its 153 cluster sizes are both 73,144. The run is a custom
dataset "downsampled to 73144 cells (K=500 per cluster from the 5 superclusters)", and 1,155,822 is the
sum of the five source supercluster totals, so the field reports the source size rather than what was
analyzed. It is outside the comparison below because it does not join. Everywhere else `filtered_cell_count` is a faithful record of what each run analyzed,
and any disagreement with the harvester is a genuine cross-source difference rather than a
bookkeeping error inside a run.

### Why the small shortfalls happen

Splitting on whether the run removed any cells at all — `summary_before_filter.n_obs` vs
`filtered_cell_count` — separates two populations:

| Population | Datasets | Exact | Short | Exceeds |
|---|---|---|---|---|
| Run removed nothing (already wholly normal upstream, or unfiltered) | 31 | 29 | 0 | 2 (Guo, retina Li) |
| Run filtered down to the normal subset | 53 | 25 | 28 | 0 |

Every shortfall is in the second group, and **every shortfall dataset has a small minimum
post-filter cluster size** (5–21 cells), while exact-match datasets range up to 1,696. The clearest
cases are the single-cell deltas:

| Dataset | delta | min cluster size after |
|---|---|---|
| `bone_marrow-Wells-Nat Immunol-2025-74e9e1` | −1 | 21 |
| `kidney-Stewart-Science-2019-de3575` | −1 | 10 |
| `kidney-Young-Science-2018-57f337` | −1 | 10 |
| `liver-Wells-Nat Immunol-2025-74e9e1` | −1 | 5 |

This is consistent with a **minimum-cells-per-cluster threshold** discarding clusters left with only
a few cells once the normal-disease filter is applied: the harvester counts cells, the pipeline
counts cells *in surviving clusters*.

**This explanation is inferred, not confirmed.** No configuration file in the repository records a
minimum cluster size, so the threshold value could not be read directly — the evidence is the
uniform association between shortfalls and small surviving clusters across all 28 cases. Confirming
it requires the `sc-nsforest-qc-nf` pipeline configuration.

## The two discrepancies

Two datasets analyze *more* cells than the harvester says exist in the normal subset. Both are runs
that removed nothing.

### `respiratory_system-Guo-Nat Commun-2023.0-3058a2` — probable filter failure

| Field | Value |
|---|---|
| `normal_cell_count` (harvester) | 332,335 |
| `total_cell_count` (harvester) | 347,970 |
| `filtered_cell_count` (summary) | **347,970** |
| `filter_normal` (harvester) | `True` |
| `disease` (summary) | `normal` |
| `summary_before_filter.n_obs` | 347,970 — the run removed nothing |

The run analyzed exactly the *total* count, not the normal count. **15,635 non-normal cells appear
to have been included in a run flagged as normal-filtered**, and the resulting NSForest markers,
f-scores, and silhouette values are computed over that mixed population.

This is worth raising upstream. The same Guo dataset also carries the `2023.0` year artifact in its
folder and file tokens, so it may have taken an unusual path through the harvester.

### `retina-Li-bioRxiv-2023-c44109` — the same pattern, unresolved

| Field | Value |
|---|---|
| `normal_cell_count` (harvester) | 3,137,294 |
| `total_cell_count` (harvester) | 3,177,310 |
| `filtered_cell_count` (summary) | **3,177,310** |
| `filter` / `nsforest_input` (summary) | `False` / `unfiltered` |
| `disease_ontology_summary` (summary) | `PATO:0000461: 3177310` — every cell normal |
| delta | **+40,016 (101.28%)** |

The run analyzed exactly the harvester's *total*, which is the Guo signature. It is not the same
puzzle, though: the run's own disease rollup counts all 3,177,310 cells as normal, so either the
rollup and the harvester define "normal" differently, or one of them is wrong. The repository cannot
say which. The earlier retina run (`cbd4aa`, removed 2026-10-26) overshot by only 7,675 cells and had
filtered; this one did not filter at all. Worth asking the maintainer whether the retina run was meant
to be filtered to normal.

## Datasets that cannot be checked

**Retina is now resolved.** As of upstream #369 the harvester carries a `homo_sapiens_retina_harvester_final.csv`
row for the run's `dataset_version_id` (`829243b7`), so retina joins and appears above. Before that, the
harvester knew only `25f1558d`, a different version of the same CELLxGENE dataset.

**Neocortex still does not join.** The run's `dataset_version_id` is the 64-hex sha256 of a custom h5ad
(`f52998989531…b237c`), which is in no harvester file. The harvester's ETL-readable file
(`homo_sapiens_neocortex_harvester_final.csv`) and the reference mapping carry the same five 2023
supercluster IDs (`3280113b`, `c4959ded`, `0476ef54`, `8b09695a`, `f72b8175`), so those two agree with
each other but not with the run. The run's `filtered_cell_count` (1,155,822) is the sum of the five
source supercluster totals (the `normal_cell_count` sum is 516,565); the analyzed count is 73,144. Even
with a matching ID the comparison would be between the source datasets and a 73,144-cell downsample.
Reconciling it needs the maintainer to say which IDs are authoritative.

## Other harvester data-quality issues surfaced

1. **Two kinds of placeholder.** 269 rows carry `normal_cell_count = 0` (all in
   `*_with_normal_counts.csv`) and a further 167 carry an *empty* value — all of them in the neocortex index file
   `homo_sapiens_neocortex_harvester.csv` (the retina index file that held the rest was replaced by
   upstream #369). The script treats both as absent.
2. **Five genuine conflicts between harvester files, all in respiratory system.** Setting placeholders
   aside, five datasets get materially different normal counts from `_final.csv` and
   `_with_normal_counts.csv`, and `_final` is larger every time:

   | `dataset_version_id` | dataset | `_final` | `_with_normal_counts` | summary follows |
   |---|---|---|---|---|
   | `4cb45d80` | Sikkema Nat Med 2023 | 579,285 | 461,098 | `_final` (exact) |
   | `018a8104` | Xu Cell 2023 | 318,426 | 260,254 | `_final` (exact) |
   | `7c98dadf` | Wells Nat Immunol 2025 | 213,154 | 186,415 | `_final` (exact) |
   | `769fff4f` | Madissoon Nat Genet 2023 | 193,108 | 157,352 | `_final` (exact) |
   | `170408c8` | Berg J Cyst Fibros 2025 | 80,624 | 24,820 | `_final` (short by 14) |

   The consistent direction suggests the two files were generated against different tissue or disease
   criteria rather than one being stale. Every analyzed run follows `_final`, so the reconciliation is
   unaffected — but the pair should not be treated as interchangeable, and only respiratory system is
   affected.
3. **Kidney has no `*_with_normal_counts.csv`** file, and carries two near-identical finals:
   `homo_sapiens_kidney_harvester_final.csv` and the misspelled
   `homo_sapiens_kidney_havester_final.csv`, 9 rows each.

## Output columns

`cell_count_reconciliation.csv` — 85 rows, 21 columns, sorted worst-discrepancy first. Filter on
`status != 'unjoined'` for the 84-row comparison proper.

| Column | Meaning |
|---|---|
| `organ`, `results_folder`, `first_author`, `dataset_version_id` | identity |
| `harvester_files`, `harvester_normal_values` | every candidate row and its `normal_cell_count`, in file order — audit trail for the placeholder rule |
| `normal_cell_count`, `total_cell_count` | harvester side (normal = largest non-zero candidate) |
| `filtered_cell_count` | summary side |
| `delta`, `pct_of_normal`, `status` | `filtered − normal`; `exact` / `short` / `exceeds` / `unjoined` |
| `run_removed_cells` | `no` if `summary_before_filter.n_obs == filtered_cell_count` |
| `summary_before_filter_n_obs`, `summary_normal_n_obs`, `sum_cluster_sizes_after` | pipeline-side cross-checks |
| `n_clusters_before`, `n_clusters_after`, `min_cluster_size_after` | evidence for the threshold hypothesis |
| `filter`, `disease` | filter flag and disease composition from the summary |
