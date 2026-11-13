#!/usr/bin/env python3
"""Reconcile harvester normal_cell_count against summary filtered_cell_count.

Run from the repository root. Writes cell_count_reconciliation.csv.
"""
import csv, glob, os, collections

csv.field_size_limit(10 ** 9)

def as_int(v):
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None

# ---- harvester rows, indexed by (organ, dataset_version_id) -----------------
H = collections.defaultdict(list)
for path in sorted(glob.glob('data/prod/*/cellxgene-harvester/*.csv')):
    if '/uberon_' in path:
        continue
    organ = path.split('/')[2]
    for row in csv.DictReader(open(path, newline='')):
        dvid = (row.get('dataset_version_id') or '').strip()
        if dvid:
            H[(organ, dvid)].append({
                'file': os.path.basename(path),
                'normal': as_int(row.get('normal_cell_count')),
                'total': as_int(row.get('total_cell_count')),
                'filter_normal': (row.get('filter_normal') or '').strip(),
            })

# ---- one row per master_dataset_summary ------------------------------------
def first_col(dirname, pattern, column, exclude_before=False):
    hits = sorted(glob.glob(os.path.join(dirname, pattern)))
    if exclude_before:
        hits = [h for h in hits if 'before_filter' not in os.path.basename(h)]
    if not hits:
        return None
    rows = list(csv.DictReader(open(hits[0], newline='')))
    return as_int(rows[0][column]) if rows else None

def cluster_sizes(dirname, before):
    pattern = 'cluster_sizes_before_filter_*.csv' if before else 'cluster_sizes_*.csv'
    hits = sorted(glob.glob(os.path.join(dirname, pattern)))
    if not before:
        hits = [h for h in hits if 'before_filter' not in os.path.basename(h)]
    if not hits:
        return []
    out = []
    for row in list(csv.reader(open(hits[0], newline='')))[1:]:
        for value in reversed(row):
            n = as_int(value)
            if n is not None:
                out.append(n)
                break
    return out

records = []
for path in sorted(glob.glob('data/prod/*/sc-nsforest-qc-nf/results/*/master_dataset_summary_*.csv')):
    organ, folder = path.split('/')[2], path.split('/')[5]
    dirname = os.path.dirname(path)
    for row in csv.DictReader(open(path, newline='')):
        dvid = (row.get('dataset_version_id') or '').strip()
        filtered = as_int(row.get('filtered_cell_count'))
        cand = H.get((organ, dvid), [])
        # normal_cell_count == 0 is a placeholder in the *_with_normal_counts files,
        # not a measurement; prefer the largest non-zero value when they disagree.
        nonzero = sorted({c['normal'] for c in cand if c['normal']}, reverse=True)
        normal = nonzero[0] if nonzero else None
        totals = sorted({c['total'] for c in cand if c['total'] is not None}, reverse=True)
        after, before = cluster_sizes(dirname, False), cluster_sizes(dirname, True)
        sb = first_col(dirname, 'summary_before_filter_*.csv', 'n_obs')
        sn = first_col(dirname, 'summary_normal_*.csv', 'n_obs')

        if normal is None or filtered is None:
            status, delta, pct = 'unjoined', None, None
        else:
            delta = filtered - normal
            pct = round(100.0 * filtered / normal, 4) if normal else None
            status = 'exact' if delta == 0 else ('short' if delta < 0 else 'exceeds')

        records.append({
            'organ': organ,
            'results_folder': folder,
            'first_author': (row.get('first_author') or '').strip(),
            'dataset_version_id': dvid,
            'harvester_files': ' | '.join(sorted({c['file'] for c in cand})),
            'harvester_normal_values': ' | '.join(str(c['normal']) for c in
                                                  sorted(cand, key=lambda c: c['file'])),
            'normal_cell_count': normal,
            'total_cell_count': totals[0] if totals else None,
            'filtered_cell_count': filtered,
            'delta': delta,
            'pct_of_normal': pct,
            'status': status,
            'run_removed_cells': '' if sb is None or filtered is None else ('no' if sb == filtered else 'yes'),
            'summary_before_filter_n_obs': sb,
            'summary_normal_n_obs': sn,
            'sum_cluster_sizes_after': sum(after) if after else None,
            'n_clusters_before': len(before) or None,
            'n_clusters_after': len(after) or None,
            'min_cluster_size_after': min(after) if after else None,
            'filter': (row.get('filter') or '').strip(),
            'disease': (row.get('disease') or '').strip(),
        })

records.sort(key=lambda r: (r['status'] != 'exceeds', r['status'] != 'short',
                            r['delta'] if r['delta'] is not None else 0,
                            r['organ'], r['results_folder']))

with open('cell_count_reconciliation.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
    w.writeheader()
    w.writerows(records)

counts = collections.Counter(r['status'] for r in records)
print(f"wrote cell_count_reconciliation.csv — {len(records)} rows")
for k, v in counts.most_common():
    print(f"  {v:3d}  {k}")
