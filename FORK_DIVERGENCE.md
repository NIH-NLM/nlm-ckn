# Fork Divergence Summary: `Springbok-LLC/nlm-ckn` vs `NIH-NLM/nlm-ckn`

_Generated 2026-07-17, revised 2026-10-28 after the neocortex/retina data sync from
`upstream/main` (`07b2d7ca`). Compares `origin/main` (Springbok-LLC fork) against `upstream/main`
(NIH-NLM)._

## Headline

The fork has **not** structurally diverged, but it is no longer merge-current. Since the
2026-08-05 merge base (`ec287fb3`) upstream has added 12 commits, all under `data/` (retina,
neocortex, liver, kidney test data, gencode). The fork took only the neocortex and retina parts,
**by copying those trees rather than merging** (`5c9c04b2`): `data/prod/neocortex` and
`data/prod/retina` match `upstream/main` exactly, apart from the two files removed in `9ec78f62`
(§2). Kidney test data, liver and `data/prod/gencode/gene_mapping_gencode_v48.csv` were deliberately
left out for now; the gencode file will be needed later. By history the branch stands **82 commits
ahead and 13 behind** `upstream/main` (the behind count includes the deliberately-skipped commits).
A trial merge of the 8 earlier commits produced about 134 conflicts, mostly rename/delete noise from
retina and kidney results folders, so a full sync will hit the same overlap unless the fork's
remaining deletions are settled upstream.

**Nearly every divergent change is confined to `data/prod/`.** The exceptions are
`.github/pull_request_template.md` (added 2026-07-11), this file, the cell-count reconciliation
analysis (`CELL_COUNT_RECONCILIATION.md`, `cell_count_reconciliation.csv`,
`tools/reconcile_cell_counts.py`), and four CI workflow files (`docs.yml`, `package-prod-data.yml`,
`promote-to-upstream.yml`, `publish-plot-assets.yml`; see §10). Otherwise no code or tooling differs
on `main`.

Tree difference against `upstream/main` as of 2026-10-28, excluding the paths deliberately not synced
(`data/test/`, `data/prod/gencode/`, `data/prod/liver/`) and the three analysis files this commit
rewrites (`FORK_DIVERGENCE.md`, `CELL_COUNT_RECONCILIATION.md`, `cell_count_reconciliation.csv`):

```
94 files changed, 7339 insertions(+), 3596 deletions(-)
  72 deleted   14 modified   8 added
  88 under data/prod/  +  6 process and workflow files
```

Liver is excluded because it differs in 80 files that mix the fork's own liver curation with
upstream's #371 (removal of a duplicated Healthy and IFALD liver dataset). Only the duplicate's
results folder (`liver-Edgar-Hepatology Communications-2025-90971d`, dataset `feca90bb`) has been
removed here, along with its row in `homo_sapiens_liver_harvester_final.csv` (as in #371); the rest of
liver is not synced. The retina and neocortex trees contribute almost nothing: they are upstream's. What is left
under `data/prod/` is the non-reference `cluster_cid_mapping` deletions, the schema normalization, and
the respiratory-system reclassification.

So this is a *data-hygiene* divergence (plus process and CI files), not an architectural one.

## The one point of real friction

Upstream keeps **reintroducing files the fork deletes.** Concretely:

- The fork removed all **non-reference `cluster_cid_mapping` files** (placeholder copies under
  `results/<dataset>/` with a blank `manual_mapped_cid`).
- **Today: fork has 0, upstream has 81** of these in `results/` (verified 2026-10-27 against the
  sync branch and `upstream/main` at `fb459b3a`). Two of upstream's 81 are in the retina `c44109` and
  neocortex Jorstad `f52998…` run folders; the data sync brought them in and the fork removed them
  again in `9ec78f62`. Both sides carry the same 11 `reference/` mappings.
- **These two are worse than the usual redundant copy.** Each shares its basename with the curated
  `reference/` mapping. The release flattens `data/prod` to one directory and keeps the last file
  written, so either could survive. The ETL validator reports `flatten-collision`. The results copy
  has `manual_mapped_cid` and `skos` blank but `cell_ontology_id` filled, so if it survived the ETL
  would use the automatic IDs, drop the SKOS relations, and for neocortex carry a single dataset ID
  (the run's sha256) that the five-row summary no longer contains. See talking point 18.
- They keep coming back. The PR #32 upstream merge included a *revert* of an upstream
  "Remove redundant results" change, which resurfaced 9 under `heart_plus_pericardium/`; the fork
  had to re-delete them (commit `71b44807`). Upstream PR #261 then shipped an 82nd for retina Li,
  re-deleted in `67740ac6`; the 2026-08-05 retina publish shipped an 83rd. Every new pipeline
  publish adds one.

**This is the thing to settle with the maintainer:** whether non-reference `cluster_cid_mapping`
files should exist at all. If upstream agrees they're redundant, the fork's deletions should be
adopted upstream so each sync stops re-litigating them. Both sides agree on the 11 `reference/`
mapping files — those are the canonical ones.

## The functional changes, grouped

**0. Process files** (`93c0ef3c`, `760bad07`) — see also §10 for the CI workflow changes
- Added `.github/pull_request_template.md` with a `Closes #` line (auto-closes the linked issue on
  merge, moving the board card to Done) plus "What & why" / "Notes for review" sections.
- Added this file (`FORK_DIVERGENCE.md`), the running record of what the fork changes and why.

**1. Schema normalization of reference mappings** (`a0d35e3b`, `598b1d2d`)
- Normalized all 11 `reference/cluster_cid_mapping` files to a uniform schema:
  `dataset_version_id,cluster_name,skos,manual_mapped_cid,cell_ontology_id`.
- Fixed a header typo (`manual:mapped:cid` → `manual_mapped_cid`, kidney Lake), added the
  `dataset_version_id` column (sourced from `cellxgene.json`, `external-1.0.0-rc.4`), and moved
  populated `cell_ontology_id` values into `manual_mapped_cid` for retina (140 rows — labelled Xu
  at the time, in fact Li; see §3) and neocortex Jorstad (153 rows).
- The 8 already-standard files are byte-identical apart from the new column.
- **Restored by upstream 2026-10-27.** The 2026-10-26 upstream runs shipped retina and neocortex
  references with their own columns (`cellxgene_term_id`, `cell_ontology_term`), which left only 9 of
  11 uniform. Upstream's 2026-10-27 publish (#369, #370) rewrote both to the uniform schema with
  `manual_mapped_cid` populated, and all 11 `reference/` files now share it again. Upstream dropped
  `cellxgene_term_id` (which differed from `cell_ontology_id` on 4 of 140 rows) and
  `cell_ontology_term` in the process.

**2. Removal of redundant non-reference mappings** (`cc30b3ba`, `71b44807`, `67740ac6`) — the
friction point above. 81 + 9 + 1 placeholder files removed; only `reference/` mappings retained.

**3. Retina identity correction** (`13dc6222`, then reversed by `61156d26`, `a69001b5`)

This one was called wrong the first time, and the correction is the most substantive thing in the
fork. **The retina results are Li's, not Xu's.**

- `13dc6222` read the retina folder as "Li superseded by Xu", deleted the Li harvester rows, and
  renamed the curated reference mapping from the Li token to the Xu token (`5188c1`). That had the
  direction backwards.
- Upstream PR #261 (`ab2cf808`, 2026-08-02) published `retina-Li-Nat Genet-2026.0-cbd4aa/` — the
  *same analysis* as the existing `retina-Xu-Cell-2023-5188c1/`, carrying correct Li metadata.
  Same source h5ad (`li_et_al_2023_BC_RGC_RPE.subset5000.h5ad`), 383,129 cells × 35,475 genes, 135
  clusters, byte-identical `cluster_order`/`cluster_sizes` before and after filter, identical
  `results_ensg`/`results_symbols`/`markers_ensg` once sorted, and identical silhouette and f-score
  values to full precision. Of the 69 shared files, 19 are byte-identical outright; the rest differ
  only by the embedded dataset token and plot-rendering nondeterminism.
- The Xu copy's metadata was **cross-joined from the bone-marrow dataset**: `dataset_title`
  `Bone_marrow`, tissue `UBERON:0002371`, bone-marrow cell types, DOI `10.1016/j.cell.2023.11.026`.
  That dataset already lives correctly at
  `data/prod/bone_marrow/sc-nsforest-qc-nf/results/bone_marrow-Xu-Cell-2023-5188c1/` — a genuinely
  different analysis (66,613 cells, 45 `Curated_annotation` clusters) that happens to share the
  `5188c1` token. The retina folder inherited its metadata from that row.
- **Decisive evidence:** the curated reference mapping's 140 `cluster_name` values are an *exact*
  match for the Li run's 140 pre-filter clusters — including five `RPE_*` clusters that the run's
  filter drops and that no other dataset in the repo has. The mapping always described Li.
- `61156d26` deletes the mislabeled `retina-Xu-Cell-2023-5188c1/` (69 files, 351 MB).
  `a69001b5` renames the reference mapping to the `retina_Li_Nat_Genet_2026.0_..._cbd4aa` token and
  updates `dataset_version_id` on all 140 rows from `ad9529a3-…-31dee15188c1` (Xu/bone marrow) to
  `25f1558d-…-b778d8cbd4aa` (Li). The §1 schema normalization is preserved; only identity moves.
- The Li harvester rows deleted in `13dc6222` stay deleted: upstream's
  `homo_sapiens_retina_li{,_subset5000}.csv` describe the Xu/`Bone_marrow` dataset under Li
  filenames and are the likely origin of the bad join.

**Upstream has since converged on the fork's position.** PR #267 (`bded3d4c`, 2026-08-05) removed
`results/retina-Xu-Cell-2023-5188c1/` upstream — the same deletion the fork made in `61156d26`. PR
#265 (`d93b140d`) replaced the bogus `homo_sapiens_retina_li*.csv` rows with
`homo_sapiens_retina_v2_harvester_li.csv`, carrying correct Li provenance under
`dataset_version_id` `25f1558d-…-b778d8cbd4aa`. This was the largest open item in this document and
it is now settled in both repositories.

**The dataset has also been re-run on the full object.** The 2026-08-05 publish analyzes
`li_et_al_2023_BC_RGC_RPE.combined.h5ad` (3,144,969 cells) where the 2026-08-01 publish used a
5,000-cells-per-cluster subset (383,129 cells) — same `dataset_version_id`, same 135 post-filter and
140 pre-filter clusters. The subset run is removed as superseded, and the reference mapping is
re-tokened from `2026.0` to `2026` to follow. The `.0` year artifact is fixed upstream this round.

**Superseded 2026-10-26: the whole `cbd4aa` line is gone.** Upstream published
`retina-Li-bioRxiv-2023-c44109/` (`1f4b4b94`) and then removed `retina-Li-Nat Genet-2026-cbd4aa/`
(`e8e9f0fa`, "remove old data", 136 files), and the data sync adopted both: the Nat Genet 2026
results, the fork's re-tokened `cbd4aa` reference mapping and the old Li harvester rows no longer
exist on the fork. The history above remains an accurate record of how the retina identity question
was settled, but none of it describes current state. What replaced it:
- `dataset_version_id` `829243b7-…-78222cc44109`, `year` 2023, DOI `10.1101/2023.11.07.566105`,
  collection "Single cell atlas of the human retina". Per the CELLxGENE curation API this is a 2024-09-30
  version of dataset `d6505c89`; the retired `cbd4aa` run was its current version, `25f1558d`
  (2026-06-11). Both versions have 3,177,310 cells.
- 3,177,310 cells analyzed with no filtering (`filter = False`; no before-filter outputs), 123
  clusters, smallest 39 cells.
- **Aligned with the harvester and the mapping as of upstream #369** (2026-10-27). The harvester is
  now a single `homo_sapiens_retina_harvester_final.csv` row for `829243b7`, and the reference
  mapping (`…_Li_bioRxiv_2023_…_c44109.csv`) has `dataset_version_id` `829243b7` on 123 rows that
  match the run's 123 clusters exactly. The 2026-10-26 state had a 140-row mapping for the retired
  version, 23 of whose names the run lacked.
- The run analyzed **40,016 more cells than the harvester's `normal_cell_count`** (3,177,310 vs
  3,137,294, 101.28%), although its own summary reports all 3,177,310 as `PATO:0000461` (normal). See
  talking point 19.

**4. Recovery & layout fix — neocortex Jorstad** (`a5d902cd`, `30f20ee2`, `cb73642b`)

_Superseded 2026-10-26: upstream published a real Jorstad run (#368, rerun in #370), and the data
sync replaced the recovered `v1.0.0-rc.4` results below with it. Notes on the new run follow this
list._
- Fixed a misspelled flat path (`neocortext/`) to the standard
  `neocortex/sc-nsforest-qc-nf/{reference,results}/` layout.
- Recovered per-cluster NSForest results (154 rows) from tag `v1.0.0-rc.4`; added a
  `master_dataset_summary` (5 superclusters) with `dataset_version_id`.
- Backfilled the missing `doi` column in that `master_dataset_summary` with
  `10.1126/science.adf6812` (Jorstad et al. 2023, *Science*). This file was the only summary using
  a reduced schema; all other summaries already carry `doi`. Placed before `collection_name` to
  match the canonical column order.

The replacement `results/neocortex-Jorstad-Science-2023-f52998…37c/` (75 files) differs from the
recovered version in ways that matter downstream:
- **One custom dataset, five dataset IDs.** Its `dataset_title` says "Human neocortex cross-area atlas
  downsampled to 73144 cells (K=500 per cluster from the 5 superclusters)". The folder name and file
  tokens are the 64-hex sha256 of that custom h5ad rather than a CELLxGENE UUID. Its tissue, assay,
  disease, sex and development-stage rollups are all `NA` (read as missing, so the harvester can fill
  them).
- **IDs aligned as of upstream #372** (2026-10-27, `07b2d7ca`). The master summary has one row per
  supercluster, with the five 2023-10-20 dataset versions (`3280113b`, `c4959ded`, `0476ef54`,
  `8b09695a`, `f72b8175`) that the reference mapping carries on all 153 rows and that the ETL-readable
  `homo_sapiens_neocortex_harvester_final.csv` also carries. Summary, mapping and harvester now share
  one ID set. A local run of the tuple writers (see "What a local ETL run showed") confirms the
  ETL's multi-dataset path then applies: each cell set attaches to its own supercluster's dataset
  node (22 / 49 / 48 / 19 / 15), all five nodes are flagged as reference datasets, and the harvester
  supplies their metadata.
- **The five summary rows carry per-supercluster values as of upstream #374** (2026-10-28, `4c8164ab`).
  The #372 version repeated the run's title, `filtered_cell_count` (1,155,822), 153 clusters and run-wide
  statistics on every row. #374 gives each row its own "Supercluster: …" title, cluster count
  (22 / 48 / 49 / 15 / 19, summing to 153), silhouette and f-score statistics, quality tiers, tissue,
  disease and development-stage term IDs and ontology summaries, and a distinct `dataset` token. So the
  title no longer depends on API load order (talking point 22 now applies to retina only).
- `filtered_cell_count` is now each supercluster's source size (638,941 / 185,477 / 129,495 / 108,940 /
  92,969, still summing to 1,155,822), equal to the harvester's total count, not the analyzed 73,144
  (11,000 / 23,595 / 23,552 / 6,277 / 8,720 per supercluster). The reconciliation therefore still reports
  the five rows as "exceeds" (185% to 247% of the harvester's normal count). `n_clusters` and the other
  counts are written as floats (`22.0`).
- `explorer_url` is still empty on all five rows, so the `nan` string bug (talking point 24) still
  applies to them.
- **Manifest names do not match the files.** `master_s3_manifest.csv` lists the results files with the
  short token `3b237c`, but the files on disk use the full 64-hex name. The validator reports this as
  an ERROR (`manifest-missing-file`), the only error left on `data/prod`. In an actual ETL run it is a
  non-fatal warning: the manifest is only an integrity cross-check and does not decide what loads.
- `results_ensg` now has `binary_genes` and `cluster_header` (#370), which the ETL requires and the
  2026-10-26 publish lacked.

**5. Run-folder lifecycle** (`56b64cb1`, `f1fcb75c`)
- Promoted 9 heart results out of a dated run folder (`2026-jun-05-d97160/`) to sit directly under
  `results/`; pruned older dated runs (`heart/2026-may-05-ef5103`, `pancreas/2026-jun-05-2c08cf`).
- Upstream PR #261 reintroduced the pattern (`results/2026-aug-01-a56002/`); `f1fcb75c` promotes it
  out again. The 2026-08-05 publish did it a third time (`results/2026-aug-05-9e4c71/`). No dated
  run folder exists on either `origin/main` or `upstream/main` otherwise, so the pipeline appears
  to emit them intermittently rather than by design.

Note on naming: the retina `cbd4aa` folder this note was written about is gone (§3), but the
point stands. Directory names keep upstream's literal spelling, spaces included. Spaces are
**existing repo convention**, not slips — roughly half of the results directories contain them
(44 of 85 when this was written; not recounted after the sync). The `.0` year artifact that the 2026-08-01 publish carried was fixed upstream in the
2026-08-05 publish; `respiratory_system-Guo-Nat Commun-2023.0-3058a2` is now the only folder left
with one. Note the fix is downstream of the harvester, not at the source: the v2 harvester rows
still record `year = 2026.0`, so the artifact can reappear on the next publish.
Normalizing the space here would make retina the outlier and re-litigate at every sync. The
space in paths is still a hazard for unquoted shell/Nextflow glue; that is worth raising upstream
as a repo-wide change, not a fork-local one.

**6. Smaller fixes** (`42b4d911`, `613751b7`, `6b36ebcd`)
- Corrected `h5ad_url` column value; added original mapping files; added missing
  respiratory-system files.

**7. Path consolidation — `neocortext/` → `neocortex/`** (`a5d902cd`, and the 2026-08-05 merge)

_Settled upstream: `f53750e4` (#361, 2026-10) renamed `neocortext` to `neocortex` there, and the fork
now matches. The notes below are history._
- `a5d902cd` originally corrected the misspelled `neocortext/` path. Upstream PR #265 re-created it,
  adding `neocortext/cellxgene-harvester/` and a second copy of the neocortex reference mapping, so
  `origin/main` briefly carried that mapping twice.
- Consolidated back under `neocortex/`: the harvester directory moved, the duplicate mapping removed,
  and the six `homo_sapiens_neocortext_*` basenames renamed to match the `homo_sapiens_<organ>_*`
  pattern every other organ uses (`uberon_neocortex.*` was already correct).
- Dropping the duplicate is safe — across all 153 rows the two files agree on `cluster_name`,
  `dataset_version_id` and `skos`, and the fork's `manual_mapped_cid` equals upstream's
  `cell_ontology_id` exactly. Upstream's copy carries one column the fork's does not,
  `cell_ontology_term` (human-readable labels); the uniform 5-column schema from §1 is kept and
  adopting labels repo-wide is listed as a talking point below.

**8. Cell count reconciliation** (`06a530ea`) — analysis, not curation
- Added `tools/reconcile_cell_counts.py`, `cell_count_reconciliation.csv` and
  `CELL_COUNT_RECONCILIATION.md`, comparing harvester `normal_cell_count` against summary
  `filtered_cell_count` across every organ. See that file; two findings are upstream-facing and
  appear as talking points below.

**9. UBERON root/descendant classification — respiratory system** (`523659f3`) — 2026-08-19
- The respiratory-system harvester is the only one of the ten organs run with **two** UBERON
  queries (`respiratory system`, `nose`); every other organ has a single query. Upstream's output
  records both as roots, so `uberon_respiratory_system.{csv,json}` carries `UBERON:0000004` (nose)
  at `level = root` and lists two entries in `root_terms`.
- The fork reclassifies nose as a **descendant** of `UBERON:0001004` (respiratory system):
  `root_terms` drops to the single respiratory-system entry, and the nose row's `level` changes
  from `root` to `descendant` in both files. This matches UBERON, where nose is part of the
  respiratory system, and makes all ten organ files single-rooted.
- **No terms are added or removed.** The `obo_ids` list, `terms` list and `total` (660) are
  unchanged, as is the CSV's row set; the entire diff is one CSV field, five deleted JSON lines,
  one JSON field, and a trailing newline. The nose subtree was already present in upstream's
  output, so nothing downstream of the term list changes.
- This will be reintroduced on the next harvester run unless the query configuration or the
  harvester's root-assignment logic is changed upstream.

**10. CI workflow changes** (`c01fec8b`, `00ca7a55`, `651ea296`) — 2026-08-11/12

The only divergence outside `data/prod/` and the process/analysis files. All three modify workflows
that already exist upstream; none adds or removes a workflow file.

*a. `docs.yml` — gate GitHub Pages to the upstream* (`c01fec8b`)
- The `Setup Pages` and `Upload artifact` steps and the whole `deploy` job now carry
  `if: github.repository_owner == 'NIH-NLM'`. `configure-pages` hits the Pages REST API, which
  404s on a fork that has Pages disabled, so every push to fork `main` failed the docs run.
- **Upstream behavior is unchanged** — NIH-NLM still builds and publishes the site. This is purely
  additive gating and is the safest of the three to adopt upstream.

*b. `package-prod-data.yml` — drop the per-author "small" packages* (`c01fec8b`)
- Removes the `discover-authors` and `package-small` jobs (~55 lines). `discover-authors` scanned
  every `*master_dataset_summary.csv` for distinct `first_author` values; `package-small` fanned out
  over that matrix, tarring each `data/prod` directory matching an author name with `.html`, `.svg`
  and `.pkl` excluded, and attaching each tarball to the release.
- Only the single full `prod-data-<tag>.tar.gz` remains. The workflow fires on `release: published`.
- **This is the one with real upstream consequence.** Unlike (a) it is not gated by owner, so
  adopting it means upstream releases stop carrying per-author tarballs. Worth confirming nobody
  downstream consumes them before this is upstreamed.

*c. Action version bumps* (`c01fec8b`) — `checkout` v4→v7, `setup-python` v5→v7, `configure-pages`
v4→v6, `upload-pages-artifact` v3→v5, `deploy-pages` v4→v5, `softprops/action-gh-release` v2→v3,
to clear a Node 20 deprecation warning.

*d. `promote-to-upstream.yml` — two robustness fixes* (`00ca7a55`, `651ea296`)

This workflow exists in both repos but is gated `if: github.repository_owner == 'Springbok-LLC'`, so
it is inert upstream and only ever runs on the fork. Both fixes therefore change fork behavior only,
even though the file itself now differs in the two repositories.
- `00ca7a55` replaces the GitHub compare API (`repos/NIH-NLM/nlm-ckn/compare/main...Springbok-LLC:main`)
  with a local divergence count. The compare endpoint always materializes a diff and, on a repo
  carrying `data/prod`, returns HTTP 422 "Sorry, this diff is taking too long to generate". The
  replacement does a bare `git init` plus two treeless partial fetches (`--filter=tree:0 --no-tags`)
  of the two tips and reads `git rev-list --left-right --count` — a few hundred KB, no working tree.
- `651ea296` makes PR creation idempotent. A 502 from the API gateway (run `31621460361`) let a
  create succeed server-side while reporting failure to the client; the retries then hit 422
  "already exists" and failed the job over a PR that had in fact been opened. The lookup is factored
  into a `find_existing_pr()` helper and re-checked after a failed attempt, exiting 0 if the PR
  exists; the retry loop also breaks on attempt 3 rather than sleeping before a retry it won't make.

*e. `publish-plot-assets.yml` — new, fork-only* (`8796d593`, #53) — 2026-08-19
- Added a workflow that runs on `release` and uploads the SVG/HTML plot files that
  `package-prod-data.yml` leaves out of the release tarball (about 1,840 SVG and 1,006 HTML,
  ~5.6 GB) to a shared static-assets S3 bucket, so `nlm-ckn-ui` can copy them S3-to-S3 instead of
  pulling them from git. Pages are rewritten to a single vendored `plotly.js` and stored gzipped.
- Its filename is load-bearing: the push role's trust policy pins on the workflow path, so renaming or
  moving it breaks AssumeRole until the IAM stack is updated. Per the file's own header it follows a
  proposal in `nlm-ckn-rnd`; I have not checked whether upstream has a counterpart.

## What a local ETL run showed

On 2026-10-28 I staged this branch's neocortex and retina trees as a local ETL run and ran the three
tuple writers that create dataset nodes (`NSForestTupleWriter`, `MappingTupleWriter`,
`CellxGeneTupleWriter`), using the ETL's own release extractor and a copy of its external cache. The
tuple files were inspected directly. **Not exercised:** the Java loader, ArangoDB, every other organ,
and the other tuple writers (Open Targets, Gene, UniProt). Only the retina dataset ID needed fetching;
the cache already held the five neocortex IDs.

- **The three writers agree on identity.** Dataset nodes are keyed `CSD_<dataset_version_id>__<organ>`
  by all three: five for neocortex, one for retina. Neocortex cell sets attach to their own supercluster
  (22 / 49 / 48 / 19 / 15, summing to the mapping's 153), retina has 123, and every cell type's
  exemplar edge points at the same node. All six are reference datasets. Both summary-driven writers
  agree on every attribute, and on every cell set's `cellxgene_dataset`.
- **The CELLxGENE-API writer disagrees with them on some attributes** (talking point 22): the neocortex
  dataset name (5 nodes) and, for retina, the publication, citation and collection version.
- **The ETL's manifest cross-check is only a warning at extraction**, as expected: the neocortex
  `3b237c` token is reported and processing continues.
- **Counts formatted with thousands separators** (`17,929`) appear in the deep-layer neocortex node's
  `donor_age`, `tissue_annotation` and `assay_summary` (talking point 23).
- **The summary-driven writers emit the literal string `nan`** as the `cellxgene_dataset` URL of all five
  neocortex nodes: the summary's `explorer_url` is empty, pandas reads it as NaN, and the ETL's
  `if ds_url:` test treats NaN as present (talking point 24, nlm-ckn-etl#167). The API's real URL
  overwrites it only because `cellxgene.json` loads last in the logged runs.
- **Loading the API data last repairs only the descriptive attributes.** _This run used the #372
  summary, which repeated run-level values._ Per-supercluster name, `cellxgene_dataset`, `cell_count`
  and tissue breakdown came out right, but `filtered_cell_count` (1,155,822), `cluster_summary` (153)
  and the silhouette and f-score statistics were identical on all five nodes. #374 fixed that for the
  summary; this run has not been repeated on the corrected file.

## Releases and ETL runs of this data

Each data release was run through the ETL (a Batch run named after the ETL tag, about 45 minutes), which
then opened an `ETL_VERSION` bump PR in `nlm-ckn-ui` that a person merges (it restores the dump on dev).

| nlm-ckn release | Contents | ETL release | Result |
|---|---|---|---|
| `v1.0.0-rc.11` (#56) | neocortex and retina sync | `v1.8.0-rc.6` | first run failed in Phase 2 (a local ArangoDB call timed out after 60 s, nlm-ckn-etl#169); the re-run succeeded |
| `v1.0.0-rc.12` (#57) | upstream's per-supercluster neocortex summary (#374) | `v1.8.0-rc.7` | succeeded |
| `v1.0.0-rc.13` (#58) | liver Edgar `90971d` results folder removed | none | superseded by rc.14 |
| `v1.0.0-rc.14` (#59) | `90971d` row removed from the liver harvester final file | `v1.8.0-rc.8` (with nlm-ckn-etl#172) | succeeded in 47 min |

**Stale datasets in the ETL's cache (nlm-ckn-etl#171, fixed in #172).** The CELLxGENE metadata cache is
reused across releases, and `CellxGeneTupleWriter` made a dataset node for every cached ID. When a
release dropped a dataset, its cached entry stayed and the writer minted a bare-ID node (`CSD_<id>`, no
organ) for it. Two datasets were affected: retina `25f1558d` (Li Nat Genet 2026, `cbd4aa`, replaced in
`v1.0.0-rc.11`), so retina showed two datasets where one is expected, and liver `feca90bb` (the Edgar
duplicate removed in rc.13/rc.14). The writer now skips cached IDs that no summary mentions. Checked
locally on the rc.14 data with the rc.10 cache: 88 dataset nodes, one retina, five neocortex, none stale.
Not checked: the loaded graph on dev, and whether the `v1.8.0-rc.6` and `rc.7` outputs carried the stray
retina node (they predate the fix).

## Suggested talking points for the maintainer

1. **Adopt the reference-mapping schema normalization upstream** so all 11 files share one schema
   (incl. `dataset_version_id`) — low-risk, mostly additive.
2. **Decide the fate of non-reference `cluster_cid_mapping` files.** If redundant (the fork's
   position), delete upstream and stop reverting their removal — this is the only recurring merge
   friction.
3. ~~**Fix the retina metadata cross-join at the source.**~~ **Done** — upstream PRs #265 and #267
   removed the mislabeled Xu folder and replaced the bogus Li harvester rows. Still worth checking
   whether other organs share a token the way `5188c1` did.
4. **Investigate `respiratory_system-Guo`.** Its run analyzed exactly `total_cell_count` (347,970)
   rather than `normal_cell_count` (332,335) despite `filter_normal = True`, so 15,635 non-normal
   cells appear to be included in a run flagged as normal-filtered. The only such case in the repo.
   See [CELL_COUNT_RECONCILIATION.md](CELL_COUNT_RECONCILIATION.md).
5. ~~**Neocortex: settle which `dataset_version_id`s are authoritative.**~~ **Done** — upstream #372
   split the summary into five rows with the five 2023 supercluster IDs, matching the mapping and the
   harvester. The run's own sha256 survives only in the `sha256` column and in file and folder names.
6. ~~**Consider adopting `cell_ontology_term` repo-wide.**~~ **Moot** — upstream dropped the column from
   the neocortex reference in #370, so all 11 files are uniform again.
7. ~~**Stop the misspelled `neocortext/` path from returning.**~~ **Done** — upstream #361 renamed it.
8. **Confirm the remaining curation calls**: the Jorstad recovery and the dated-run promotion
   convention.
9. **Consider adopting the PR template upstream** so contributions across both repos use the same
   `Closes #` convention.
10. **Make the respiratory-system harvester single-rooted at the source.** The `nose` query is
   recorded as a second root, but nose is part of the respiratory system in UBERON and every other
   organ file has exactly one root. Either drop the redundant query or have the harvester classify
   a query term that resolves under an existing root as a descendant — otherwise §9 has to be
   re-applied after every run.
11. **Upstream the `docs.yml` Pages gate** (§10a). It is a no-op on NIH-NLM and stops the docs
   workflow failing on every fork push — the cheapest of the CI items to settle.
12. **Decide whether per-author release tarballs are still wanted** (§10b). The fork has removed
   the `package-small` matrix; adopting that upstream changes what a release ships, so it needs a
   deliberate call rather than a silent sync.
13. **Upstream the two `promote-to-upstream.yml` fixes** (§10d). The workflow is inert on NIH-NLM,
   so adopting them costs nothing there and keeps the two copies of the file from drifting.
14. **Raise Git LFS before more organs land.** No `.gitattributes` exists anywhere. The retina Li
   publish alone shipped two 62 MB `.svg.tar.gz` files and four 3.7–7.4 MB pickles; `.pkl` is also
   version-fragile as an archival format. Cheaper to settle now than after the next ten datasets.
15. ~~**Retina: make the reference mapping and the run agree.**~~ **Done** — #369 rewrote the mapping to
   the run's 123 clusters with `dataset_version_id` `829243b7`.
16. **Neocortex: report the analyzed cell count.** `filtered_cell_count` is each supercluster's source
   size (the harvester's total count; the five sum to 1,155,822), while the run analyzed 73,144
   downsampled cells (K=500 per cluster). Put the per-supercluster analyzed count in
   `filtered_cell_count` (or add a separate field for the source size), so the reconciliation can compare
   like with like.
17. **Make the manifest match the files.** The neocortex manifest lists the short token `3b237c` while the
   files and folder use the full 64-hex name; this is the one remaining validator ERROR (a non-fatal
   warning in an actual ETL run). The run's 64-hex sha256 is also still the folder and file token where
   every other dataset uses a 6-hex suffix.
18. **Stop publishing a second `cluster_cid_mapping` in each run folder, or have the ETL prefer
   `reference/`.** The retina `c44109` publish (`1f4b4b94`, 2026-10-25) and the neocortex publish (#368) each
   added a results-folder mapping with the same basename as the reference one (blank
   `manual_mapped_cid` and `skos`, filled `cell_ontology_id`), and #369 and #370 rewrote them. After the release
   flatten only one survives, which is why the validator reports `flatten-collision`. The fork
   deletes them (`9ec78f62`). Related: the loader reads tuples files in unsorted `Files.list` order, so
   when two writers set the same attribute on a dataset node the winner depends on the filesystem
   (nlm-ckn-etl#166, with a follow-up comment on why "load `cellxgene.json` first" is a trade-off, see
   point 22).
19. **Retina: explain the 40,016-cell overshoot.** The run analyzed all 3,177,310 cells with
   `filter = False`, while the harvester's `normal_cell_count` is 3,137,294. The summary's own
   disease rollup reports every cell as normal, so one of the two sources is wrong, or the harvester
   counts "normal" differently. The same pattern as `respiratory_system-Guo` (point 4).
20. **Harvester files the ETL does not read.** The ETL reads only `*_harvester_final.csv`. The heart
   files (`…_heart_plus_pericardium_final.csv`, no `harvester`) and respiratory Guo
   (`…_harvester_guo.csv`) do not match, so those 8 datasets get no harvester metadata (donor counts,
   disease status, collection version). Those 8 (7 heart and Guo) are the only datasets of 85 with no
   harvester row since upstream #372 aligned the neocortex IDs.
21. ~~**Neocortex: give each supercluster row its own values.**~~ **Done** — upstream #374 (2026-10-28)
   gave each of the five rows its own title, cluster count, statistics and ontology summaries. What
   remains is the analyzed cell count (talking point 16) and the empty `explorer_url` (talking point 24).

22. **Decide attribute precedence between the CELLxGENE API and the summary.** The three dataset-node
   writers set some of the same attributes to different values, and the loader keeps whichever file it
   reads last (unsorted `Files.list` order; in the 2026-07-27 release log `cellxgene.json` was 102nd of
   113, after the NSForest and mapping files — but those logs are local macOS runs (paths under
   `/Users/…`), and the production release runs in a Linux container whose order is not known). Observed conflicts: neocortex `dataset_name` / `Name`
   (API "Supercluster: IT-projecting excitatory neurons" etc. vs the summary's repeated run title, 5
   nodes; resolved for neocortex by #374, whose titles now match the API), and retina `publication` / `Citation` (API `10.1038/s41588-025-02454-1`, "Li (2026) Nat Genet",
   because it reports the dataset's *current* collection, vs the summary's `10.1101/2023.11.07.566105`,
   "Li (2023) bioRxiv") and `dataset_collection_version`. The retina node's `described_in` edge targets
   the 2026 paper whatever the order. With the API last, neocortex gets the better names and retina is
   labelled with a paper published after its dataset version; with the summary last it is the reverse.
   Posted on nlm-ckn-etl#166.
23. **Harvester count formatting.** The deep-layer neocortex row (`c4959ded`) has thousands separators
   in `donor_age`, `tissue_annotation` and `assay_summary` (`UBERON:0009835: 17,929`), where the other
   four use plain integers. The ETL copies them verbatim onto the dataset node, so a consumer parsing
   those counts would handle that node differently.

24. **`nan` written as a string in dataset nodes** (nlm-ckn-etl#167). `build_cell_set_dataset` tests
   `if ds_url:`, `if coll_url:` and `dataset_title or collection_name` on values pandas reads as NaN
   when a summary cell is blank; NaN is truthy, so `"nan"` is emitted. Today only the five neocortex rows
   (empty `explorer_url`) trigger it, of 85 summaries. Order-independent correctness needs the NaN checks
   fixed in the ETL as well as the load order (point 22) and per-supercluster summary values (point 21);
   until then the API's URL happens to mask it.
---

These are all upstreamable as PRs; nothing here is a hard fork.

## Appendix: divergent functional commits

| Commit | Date | Summary |
|---|---|---|
| `57dadefb` | 2026-10-29 | Remove the duplicate Edgar 90971d row from the liver harvester final file |
| `3a76da29` | 2026-10-29 | Remove duplicate liver Edgar 90971d results folder |
| `d85a31fa` | 2026-10-28 | Take upstream's corrected neocortex master_dataset_summary (#374) |
| `9ca5c4c0` | 2026-10-28 | Take upstream's corrected neocortex master_dataset_summary (#372) |
| `9ec78f62` | 2026-10-27 | Remove results-folder cluster_cid_mapping for retina c44109 and neocortex Jorstad |
| `5c9c04b2` | 2026-10-27 | Sync neocortex and retina data with upstream/main (drops retina `cbd4aa`) |
| `8796d593` | 2026-08-19 | Add publish-plot-assets workflow (#53) |
| `523659f3` | 2026-08-19 | Make nose a respiratory system descendant |
| `651ea296` | 2026-08-12 | promote-to-upstream: re-check for an existing PR before failing (#52) |
| `00ca7a55` | 2026-08-12 | promote-to-upstream: count divergence with git, not the compare API (#49) |
| `c01fec8b` | 2026-08-11 | Drop per-author packages; gate Pages to NIH-NLM; bump action versions (#48) |
| `06a530ea` | 2026-08-05 | Add cell count reconciliation analysis and refresh for #265/#267 |
| `b59dc212` | 2026-08-05 | Consolidate neocortext/ into neocortex/ |
| `36f022cd` | 2026-08-05 | Re-token retina reference mapping to the 2026 dataset token _(superseded 2026-10-26)_ |
| `a9d97ca6` | 2026-08-05 | Remove retina Li subset run superseded by the full-dataset run _(superseded 2026-10-26)_ |
| `f93180b8` | 2026-08-05 | Remove non-reference cluster_cid_mapping for retina Li full run _(superseded 2026-10-26)_ |
| `a6e2f013` | 2026-08-05 | Promote retina Li full-dataset results out of dated run folder _(superseded 2026-10-26)_ |
| `a69001b5` | 2026-08-03 | Re-token retina reference mapping to the Li cbd4aa dataset _(superseded 2026-10-26)_ |
| `61156d26` | 2026-08-03 | Remove mislabeled retina Xu results (duplicate of retina Li cbd4aa) _(superseded 2026-10-26)_ |
| `67740ac6` | 2026-08-03 | Remove non-reference cluster_cid_mapping for retina Li _(superseded 2026-10-26)_ |
| `f1fcb75c` | 2026-08-03 | Promote retina Li results out of dated run folder _(superseded 2026-10-26)_ |
| `1f74b5cc` | 2026-07-17 | Backfill missing doi in neocortex Jorstad master_dataset_summary _(superseded 2026-10-26)_ |
| `760bad07` | 2026-07-17 | Add fork divergence summary (origin vs upstream) |
| `93c0ef3c` | 2026-07-11 | Add a PR template with a Closes line |
| `71b44807` | 2026-06-14 | Remove heart non-reference cluster_cid_mapping files (reintroduced upstream) |
| `598b1d2d` | 2026-06-13 | Move cell_ontology_id into manual_mapped_cid for retina Xu and neocortex Jorstad |
| `a0d35e3b` | 2026-06-13 | Normalize all 11 reference cluster_cid_mapping files to a uniform schema |
| `cb73642b` | 2026-06-13 | Add dataset_version_id column to neocortex Jorstad master_dataset_summary _(superseded 2026-10-26)_ |
| `30f20ee2` | 2026-06-13 | Add master_dataset_summary for neocortex Jorstad (5 superclusters) _(superseded 2026-10-26)_ |
| `a5d902cd` | 2026-06-13 | Recover neocortex Jorstad results_ensg from v1.0.0-rc.4; normalize layout _(superseded 2026-10-26)_ |
| `13dc6222` | 2026-06-13 | Remove retina Li data (superseded by Xu); rename reference mapping to Xu _(superseded 2026-10-26)_ |
| `cc30b3ba` | 2026-06-13 | Remove non-reference cluster_cid_mapping files |
| `56b64cb1` | 2026-06-13 | Promote heart results from dated run folder; prune older dated runs |
| `42b4d911` | 2026-06-12 | Use correct h5ad_url column value |
| `613751b7` | 2026-06-12 | Add original mapping files |
| `6b36ebcd` | 2026-06-12 | Add missing respiratory system files |
