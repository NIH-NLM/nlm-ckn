#!/usr/bin/env python3
"""
Generate Sphinx RST pages from nlm-ckn master_dataset_summary.csv files.

This script:
1. Finds the latest sc-nsforest-qc-nf/results/{date-id}/ run per tissue
2. Groups all datasets by tissue
3. Generates per-tissue RST pages with summary tables and reference forms
4. Generates the main index.rst landing page

Usage:
    python docs/generate_pages.py
"""

import csv
import glob
import os
from pathlib import Path

# Paths relative to repo root
GITHUB_RAW = "https://raw.githubusercontent.com/NIH-NLM/nlm-ckn/main"
GITHUB_PREVIEW = "https://htmlpreview.github.io/?https://github.com/NIH-NLM/nlm-ckn/blob/main"

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data" / "prod"
DOCS_DIR = REPO_ROOT / "docs"
TISSUES_DIR = DOCS_DIR / "tissues"

# Columns to extract from CSV
COLUMNS = [
    "collection_name",
    "collection_url",
    "dataset_title",
    "explorer_url",
    "first_author",
    "year",
    "n_clusters",
    "n_cells",
    "median_silhouette",
    "mean_silhouette",
    "median_fscore",
    "mean_fscore",
    "organ",
    "dataset",
]

# Subdirs of data/prod/ that are not anatomical tissue runs
SKIP_DIRS = {"biomart", "ontology_lookup_server"}


def find_latest_run_roots() -> dict[str, Path]:
    """Return the latest sc-nsforest-qc-nf/results/{date-id}/ run per tissue."""
    latest_runs: dict[str, Path] = {}
    for tissue_dir in sorted(DATA_DIR.iterdir()):
        if not tissue_dir.is_dir() or tissue_dir.name in SKIP_DIRS:
            continue
        results_dir = tissue_dir / "sc-nsforest-qc-nf" / "results"
        if not results_dir.is_dir():
            continue
        candidates = [d for d in results_dir.iterdir()
                      if d.is_dir() and not d.name.startswith('.')]
        if candidates:
            latest = max(candidates, key=lambda p: p.stat().st_mtime)
            latest_runs[tissue_dir.name] = latest
            print(f"  {tissue_dir.name}: run → {latest.name}")
    return latest_runs


def find_datasets_in_run(run_root: Path) -> list[Path]:
    """Return sorted dataset directories within a run root."""
    return sorted(d for d in run_root.iterdir()
                  if d.is_dir() and not d.name.startswith('.'))


def find_files_in_dataset(dataset_dir: Path) -> dict[str, list[Path]]:
    """Return all relevant files in a dataset directory, grouped by type."""
    return {
        "csv":  sorted(dataset_dir.glob("*master_dataset_summary.csv")),
        "html": sorted(dataset_dir.glob("*.html")),
        "svg":  sorted(dataset_dir.glob("*.svg")),
    }


def github_url(filepath: str) -> str:
    """Build a GitHub URL for a file in the repo."""
    rel = os.path.relpath(filepath, REPO_ROOT)
    if filepath.endswith('.html'):
        return f"{GITHUB_PREVIEW}/{rel}"
    return f"{GITHUB_RAW}/{rel}"


def read_csv_row(csv_path: str) -> dict | None:
    """Read the first data row from a master_dataset_summary.csv."""
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row
    return None


def format_number(val) -> str:
    """Format a number string nicely."""
    try:
        num = float(val)
        if num == int(num) and num > 1:
            return f"{int(num):,}"
        return f"{num:.4f}"
    except (ValueError, TypeError):
        return str(val)


def get_tissue_label(tissue_name: str) -> str:
    """Convert tissue directory name to a display label."""
    return tissue_name.replace("_", " ").title()


def avg_score(datasets: list, key: str) -> str:
    """Compute average of a score field across datasets."""
    vals = []
    for ds in datasets:
        try:
            vals.append(float(ds.get(key, 0)))
        except (ValueError, TypeError):
            pass
    if not vals:
        return "N/A"
    return f"{sum(vals) / len(vals):.4f}"


def generate_tissue_rst(tissue: str, datasets: list) -> str:
    """Generate RST content for a single tissue page."""
    label = get_tissue_label(tissue)
    lines = []

    # Title
    lines.append("=" * len(label))
    lines.append(label)
    lines.append("=" * len(label))
    lines.append("")
    lines.append(f"Datasets analyzed for **{label}**: {len(datasets)} total.")
    lines.append("")

    # --- Dataset Summary Table ---
    lines.append("Dataset Summary")
    lines.append("-" * len("Dataset Summary"))
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    lines.append("   <div class=\"table-wrapper\">")
    lines.append("   <table class=\"dataset-summary\">")
    lines.append("   <thead>")
    lines.append("   <tr>")
    lines.append("     <th>Dataset</th>")
    lines.append("     <th>Collection</th>")
    lines.append("     <th>Dataset Title</th>")
    lines.append("     <th>Explorer</th>")
    lines.append("     <th>Cells</th>")
    lines.append("     <th>Clusters</th>")
    lines.append("     <th>Med. Silhouette</th>")
    lines.append("     <th>Mean Silhouette</th>")
    lines.append("     <th>Med. F-score</th>")
    lines.append("     <th>Mean F-score</th>")
    lines.append("     <th>Report</th>")
    lines.append("   </tr>")
    lines.append("   </thead>")
    lines.append("   <tbody>")

    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        year = ds.get("year", "")
        journal = ds.get("journal", "")
        dataset_label = f"{author} ({journal}) {year}" if journal else f"{author} {year}"
        collection_url = ds.get("collection_url", "#")
        dataset_title = ds.get("dataset_title", "")
        dt_display = dataset_title[:50] + "..." if len(dataset_title) > 50 else dataset_title
        explorer_url = ds.get("explorer_url", "#")
        collection_name = ds.get("collection_name", "")
        n_cells = format_number(ds.get("n_cells", ""))
        n_clusters = format_number(ds.get("n_clusters", ""))
        med_sil = format_number(ds.get("median_silhouette", ""))
        mean_sil = format_number(ds.get("mean_silhouette", ""))
        med_f = format_number(ds.get("median_fscore", ""))
        mean_f = format_number(ds.get("mean_fscore", ""))
        report_link = ""
        if ds.get("_report_url"):
            report_link = f'<a href="{ds["_report_url"]}" target="_blank">View Report</a>'
        coll_display = collection_name[:50] + "..." if len(collection_name) > 50 else collection_name

        lines.append("   <tr>")
        lines.append(f'     <td><strong>{dataset_label}</strong></td>')
        lines.append(f'     <td><a href="{collection_url}" target="_blank" title="{collection_name}">{coll_display}</a></td>')
        lines.append(f'     <td title="{dataset_title}">{dt_display}</td>')
        lines.append(f'     <td><a href="{explorer_url}" target="_blank">Explore</a></td>')
        lines.append(f"     <td>{n_cells}</td>")
        lines.append(f"     <td>{n_clusters}</td>")
        lines.append(f"     <td>{med_sil}</td>")
        lines.append(f"     <td>{mean_sil}</td>")
        lines.append(f"     <td>{med_f}</td>")
        lines.append(f"     <td>{mean_f}</td>")
        lines.append(f"     <td>{report_link}</td>")
        lines.append("   </tr>")

    lines.append("   </tbody>")
    lines.append("   </table>")
    lines.append("   </div>")
    lines.append("")

    # --- Per Dataset Visualizations ---
    lines.append("Visualizations")
    lines.append("-" * len("Visualizations"))
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        journal = ds.get("journal", "")
        year = ds.get("year", "")
        dt = ds.get("dataset_title", "")
        label = f"{author} ({journal}) {year} - {dt}" if journal else f"{author} {year} - {dt}"

        viz_files = ds.get("_viz_files", [])
        if not viz_files:
            continue

        lines.append(f'   <details><summary><strong>{label}</strong></summary>')
        lines.append('   <div class="viz-links">')

        categories = {
            "Quality Boxplots": [f for f in viz_files if "boxplot_" in os.path.basename(f)],
            "Scatter Plots":    [f for f in viz_files if "scatter_" in os.path.basename(f)],
            "Distributions":    [f for f in viz_files if "distribution_" in os.path.basename(f)],
            "Gene Expression":  [f for f in viz_files if any(x in os.path.basename(f) for x in ["dotplot", "matrixplot"])],
            "Violin Plots":     [f for f in viz_files if "stacked_violin" in os.path.basename(f)],
            "Histograms":       [f for f in viz_files if "hist_" in os.path.basename(f)],
            "Dendrogram":       [f for f in viz_files if "dendrogram" in os.path.basename(f)],
            "Summary":          [f for f in viz_files if "silhouette_fscore" in os.path.basename(f)],
        }
        for cat_name, files in categories.items():
            if files:
                links = " | ".join(
                    f'<a href="{github_url(f)}" target="_blank">{os.path.basename(f)}</a>'
                    for f in sorted(files)
                )
                lines.append(f'   <p><strong>{cat_name}:</strong> {links}</p>')

        lines.append('   </div>')
        lines.append('   </details>')

    lines.append("")

    # --- Reference Selection Form ---
    lines.append("Reference Selection Form")
    lines.append("-" * len("Reference Selection Form"))
    lines.append("")
    lines.append("Use this form to select a reference dataset for this organ, add your name and notes, then download the selection as a CSV file.")
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    lines.append(f'   <div class="reference-form" id="form-{tissue}">')
    lines.append(f'   <h3>Reference Selection: {label}</h3>')
    lines.append(f'   <label for="reviewer-{tissue}"><strong>Your Name:</strong></label><br>')
    lines.append(f'   <input type="text" class="reviewer-name" id="reviewer-{tissue}" placeholder="Enter your name">')
    lines.append('   <br><br>')
    lines.append('   <table class="reference-table">')
    lines.append("   <thead>")
    lines.append("   <tr>")
    lines.append("     <th>Reference?</th>")
    lines.append("     <th>Dataset</th>")
    lines.append("     <th>Author</th>")
    lines.append("     <th>Year</th>")
    lines.append("     <th>Notes</th>")
    lines.append("   </tr>")
    lines.append("   </thead>")
    lines.append("   <tbody>")

    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        year = ds.get("year", "")
        dataset_name = ds.get("dataset", "")
        collection_url = ds.get("collection_url", "")
        explorer_url = ds.get("explorer_url", "")

        lines.append(f'   <tr class="dataset-row" '
                     f'data-dataset="{dataset_name}" '
                     f'data-author="{author}" '
                     f'data-year="{year}" '
                     f'data-collection-url="{collection_url}" '
                     f'data-explorer-url="{explorer_url}">')
        lines.append(f'     <td><input type="checkbox" class="ref-checkbox" data-tissue="{tissue}"></td>')
        lines.append(f'     <td>{dataset_name}</td>')
        lines.append(f"     <td>{author}</td>")
        lines.append(f"     <td>{year}</td>")
        lines.append(f'     <td><input type="text" class="notes-input" placeholder="Add notes..."></td>')
        lines.append("   </tr>")

    lines.append("   </tbody>")
    lines.append("   </table>")
    lines.append(f'   <button class="download-csv-btn" data-tissue="{tissue}">Download CSV</button>')
    lines.append("   </div>")
    lines.append("")

    return "\n".join(lines)


def generate_index_rst(tissues: dict) -> str:
    """Generate the main index.rst with toctree."""
    label = "Cell Knowledge Network (Cell-KN)"
    lines = []
    lines.append("=" * len(label))
    lines.append(label)
    lines.append("=" * len(label))
    lines.append("")
    lines.append("Welcome to the Cell Knowledge Network dataset quality dashboard.")
    lines.append("This site presents silhouette and F-score quality metrics for single-cell")
    lines.append("RNA-seq datasets across multiple human tissues, harvested from CellxGene.")
    lines.append("")
    lines.append("Select a tissue below to view dataset summaries, quality scores, and")
    lines.append("interactive Plotly reports. You can also select a reference dataset per")
    lines.append("tissue and download your selections as a CSV.")
    lines.append("")

    lines.append("Tissue Overview")
    lines.append("-" * len("Tissue Overview"))
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: 30 15 20 20")
    lines.append("")
    lines.append("   * - Tissue")
    lines.append("     - Datasets")
    lines.append("     - Avg Median Silhouette")
    lines.append("     - Avg Median F-score")

    for tissue_name, datasets in sorted(tissues.items()):
        tissue_label = get_tissue_label(tissue_name)
        lines.append(f"   * - :doc:`tissues/{tissue_name}`")
        lines.append(f"     - {len(datasets)}")
        lines.append(f"     - {avg_score(datasets, 'median_silhouette')}")
        lines.append(f"     - {avg_score(datasets, 'median_fscore')}")

    lines.append("")
    lines.append(".. toctree::")
    lines.append("   :maxdepth: 2")
    lines.append("   :caption: Tissues")
    lines.append("   :hidden:")
    lines.append("")
    for tissue_name in sorted(tissues.keys()):
        lines.append(f"   tissues/{tissue_name}")
    lines.append("")

    return "\n".join(lines)


def main():
    print("NLM-CKN Sphinx Page Generator")
    print("=" * 40)

    TISSUES_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: find the latest run root per tissue
    print("\nDiscovering latest run per tissue...")
    latest_runs = find_latest_run_roots()

    # Step 2: collect all datasets from the latest run of each tissue
    tissues: dict[str, list] = {}
    for tissue, run_root in sorted(latest_runs.items()):
        for dataset_dir in find_datasets_in_run(run_root):
            files = find_files_in_dataset(dataset_dir)
            if not files["csv"]:
                continue
            row = read_csv_row(str(files["csv"][0]))
            if not row:
                print(f"  WARNING: Empty CSV in {dataset_dir}")
                continue
            all_viz = files["html"] + files["svg"]
            row["_viz_files"] = [str(f) for f in all_viz]
            summary_html = [f for f in files["html"]
                            if "silhouette_fscore_summary" in f.name]
            row["_report_url"] = github_url(str(summary_html[0])) if summary_html else ""
            tissues.setdefault(tissue, []).append(row)

    print(f"\nFound {len(tissues)} tissues:")
    for t, ds in sorted(tissues.items()):
        print(f"  {t}: {len(ds)} datasets")

    # Step 3: generate per-tissue RST files
    for tissue, datasets in sorted(tissues.items()):
        rst_path = TISSUES_DIR / f"{tissue}.rst"
        rst_path.write_text(generate_tissue_rst(tissue, datasets), encoding="utf-8")
        print(f"  Generated: {rst_path.name}")

    # Step 4: generate index.rst
    index_path = DOCS_DIR / "index.rst"
    index_path.write_text(generate_index_rst(tissues), encoding="utf-8")
    print(f"  Generated: index.rst")

    print(f"\nDone! Generated {len(tissues)} tissue pages + index.rst")
    print(f"Next: cd docs && make html")


if __name__ == "__main__":
    main()
