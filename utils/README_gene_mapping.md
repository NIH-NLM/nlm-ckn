# Gene Mapping Utilities

Utilities for mapping Ensembl gene IDs (ENSG) to human-readable gene symbols using the [cell-kn gene mapping file](https://github.com/NIH-NLM/cell-kn/blob/main/data/biomart/gene_mapping.csv).

## Quick Start

### Download the Utility

```bash
# Download from GitHub
curl -O https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/utils/gene_mapping_utils.py
```

Or in your notebook:

```python
import urllib.request

url = "https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/utils/gene_mapping_utils.py"
urllib.request.urlretrieve(url, "gene_mapping_utils.py")
```

## NSForest Workflow

Complete workflow for displaying readable gene names in NSForest plots:

```python
import pandas as pd
from gene_mapping_utils import load_gene_mapping, create_mapping_dict
import nsforest as ns

# Step 1: Load gene mapping
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)
print(f"Loaded {len(gene_mapping)} gene mappings")

# Step 2: Add gene symbols to adata
# This creates a column that scanpy can use to display readable names
adata.var['gene_symbol'] = [ensg_to_symbol.get(gene, gene) for gene in adata.var_names]
print("Added gene symbols to adata.var['gene_symbol']")

# Step 3: Create markers_dict with ENSG IDs
# IMPORTANT: Use NSForest_markers (ENSG IDs), not gene symbols
# This must match adata.var_names for scanpy to find the genes
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))

print(f"markers_dict created with {len(markers_dict)} clusters")

# Step 4: Plot with gene symbols displayed
# The gene_symbols='gene_symbol' parameter tells scanpy to:
# - Look up genes using ENSG IDs from markers_dict
# - Display gene symbols from adata.var['gene_symbol'] on the plot

ns.pl.dotplot(adata, markers_dict, cluster_header, 
              dendrogram=True, 
              use_raw=False,
              gene_symbols='gene_symbol',  # Display symbols on plot
              save="svg", 
              output_folder=output_folder,
              outputfilename_suffix=outputfilename_prefix)

ns.pl.stackedviolin(adata, markers_dict, cluster_header, 
                    dendrogram=True, 
                    use_raw=False,
                    gene_symbols='gene_symbol',  # Display symbols on plot
                    save="svg", 
                    output_folder=output_folder,
                    outputfilename_suffix=outputfilename_prefix)

ns.pl.matrixplot(adata, markers_dict, cluster_header, 
                 dendrogram=True, 
                 use_raw=False,
                 gene_symbols='gene_symbol',  # Display symbols on plot
                 save="svg", 
                 output_folder=output_folder,
                 outputfilename_suffix=outputfilename_prefix)
```

## How It Works

**The Problem:**
- Your AnnData object (`adata`) has ENSG IDs in `adata.var_names`
- You want plots to show readable gene symbols like "CD3D" instead of "ENSG00000167286"

**The Solution:**
1. **Add symbols to adata:** Store gene symbols in `adata.var['gene_symbol']`
2. **Keep ENSG IDs in markers_dict:** Use `results_to_plot["NSForest_markers"]` (ENSG IDs)
3. **Use gene_symbols parameter:** Tell scanpy to display symbols while looking up by ENSG

**What NOT to do:**
- Don't change `adata.var_names` from ENSG IDs
- Don't create `markers_dict` with gene symbols - scanpy won't find them

## Complete Jupyter Notebook Example

```python
# Cell 1: Download utility (one-time)
import urllib.request
import os

if not os.path.exists('gene_mapping_utils.py'):
    url = "https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/utils/gene_mapping_utils.py"
    urllib.request.urlretrieve(url, "gene_mapping_utils.py")
    print("Downloaded gene_mapping_utils.py")

# Cell 2: Load gene mapping
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)
print(f"Loaded {len(gene_mapping)} gene mappings")

# Cell 3: Add gene symbols to adata
adata.var['gene_symbol'] = [ensg_to_symbol.get(gene, gene) for gene in adata.var_names]

print("Added gene symbols to adata.var")
print(f"Example: {adata.var_names[0]} -> {adata.var['gene_symbol'].iloc[0]}")

# Cell 4: Create markers_dict with ENSG IDs
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))

print(f"markers_dict created with {len(markers_dict)} clusters")

# Cell 5: Plot with gene symbols displayed
import nsforest as ns

ns.pl.dotplot(adata, markers_dict, cluster_header, 
              dendrogram=True, 
              use_raw=False,
              gene_symbols='gene_symbol',
              save="svg", 
              output_folder=output_folder, 
              outputfilename_suffix=outputfilename_prefix)

ns.pl.stackedviolin(adata, markers_dict, cluster_header, 
                    dendrogram=True, 
                    use_raw=False,
                    gene_symbols='gene_symbol',
                    save="svg", 
                    output_folder=output_folder,
                    outputfilename_suffix=outputfilename_prefix)

ns.pl.matrixplot(adata, markers_dict, cluster_header, 
                 dendrogram=True, 
                 use_raw=False,
                 gene_symbols='gene_symbol',
                 save="svg", 
                 output_folder=output_folder,
                 outputfilename_suffix=outputfilename_prefix)
```

## Basic Usage (Non-NSForest)

For general gene mapping without scanpy/NSForest:

```python
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

# Load mapping (cached after first run for speed)
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)

# Map a list of genes
genes = ['ENSG00000167286', 'ENSG00000010610', 'ENSG00000153563']
mapped = [ensg_to_symbol.get(g, g) for g in genes]
print(mapped)
# Output: ['CD3D', 'CD4', 'CD8A']
```

## API Reference

### `load_gene_mapping(cache_file="gene_mapping.csv", use_cache=True)`

Load gene mapping file from GitHub or local cache.

**Parameters:**
- `cache_file` (str): Local filename to cache the mapping file
- `use_cache` (bool): If True, use cached file if it exists

**Returns:** pd.DataFrame with columns `ensembl_gene_id` and `external_gene_name`

---

### `create_mapping_dict(gene_mapping)`

Create ENSG ID to gene symbol mapping dictionary.

**Parameters:**
- `gene_mapping` (pd.DataFrame): Gene mapping dataframe from `load_gene_mapping()`

**Returns:** dict mapping ensembl_gene_id to external_gene_name

---

### `map_genes(gene_list, mapping_dict)`

Map a list of ENSG IDs to gene symbols.

**Parameters:**
- `gene_list` (list): List of gene identifiers (ENSG IDs or symbols)
- `mapping_dict` (dict): Dictionary from `create_mapping_dict()`

**Returns:** list of gene symbols (keeps original if mapping not found)

---

### `map_dataframe_column(df, column, mapping_dict, new_column=None)`

Map ENSG IDs in a dataframe column to gene symbols.

**Parameters:**
- `df` (pd.DataFrame): Dataframe containing gene lists
- `column` (str): Column name containing lists of ENSG IDs
- `mapping_dict` (dict): Dictionary from `create_mapping_dict()`
- `new_column` (str): Name for new column (default: `{column}_symbols`)

**Returns:** pd.DataFrame with new column containing mapped gene symbols

## Performance

| Operation | Speed | Notes |
|-----------|-------|-------|
| First run | ~2-5s | Downloads and caches gene_mapping.csv |
| Subsequent runs | ~0.2s | Loads from cached file |
| Mapping | Fast | Uses list comprehension (5-10x faster than pandas apply) |

**Tip:** The first time you run `load_gene_mapping()`, it downloads and caches the file locally. All subsequent runs load from the cache.

## Data Source

This utility uses the gene mapping file from the NIH NLM cell-kn repository:
- **Repository:** https://github.com/NIH-NLM/cell-kn
- **Mapping file:** data/biomart/gene_mapping.csv
- **Source:** BioMart Ensembl gene annotations

## Troubleshooting

### KeyError: "Could not find keys ['CD3D', 'CD4', ...] in adata.var_names"

**Problem:** You're passing gene symbols in `markers_dict`, but `adata.var_names` has ENSG IDs.

**Solution:** 
```python
# Use ENSG IDs in markers_dict
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))  # ENSG IDs

# Use gene_symbols parameter to display symbols
ns.pl.dotplot(adata, markers_dict, cluster_header, gene_symbols='gene_symbol')
```

---

### Slow performance

**Solution:** Make sure caching is enabled (default). First run downloads the file, subsequent runs are much faster.

---

### Some genes don't map

**Solution:** The function keeps the original gene ID if no mapping is found. This is expected for some genes not in the BioMart database.

## Contributing

Issues and pull requests welcome at: https://github.com/NIH-NLM/cell-kn

## License

Same as parent repository (cell-kn)
