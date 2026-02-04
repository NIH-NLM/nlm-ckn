# Quick Reference: NSForest Gene Mapping

## The Correct Way (Copy This)

```python
from gene_mapping_utils import load_gene_mapping, create_mapping_dict
import nsforest as ns

# 1. Load gene mapping
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)

# 2. Add gene symbols to adata
adata.var['gene_symbol'] = [ensg_to_symbol.get(gene, gene) for gene in adata.var_names]

# 3. Create markers_dict with ENSG IDs (NOT symbols)
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))

# 4. Plot with gene_symbols parameter
ns.pl.dotplot(adata, markers_dict, cluster_header, 
              dendrogram=True, use_raw=False,
              gene_symbols='gene_symbol',  # This is the key!
              save="svg", output_folder=output_folder,
              outputfilename_suffix=outputfilename_prefix)

ns.pl.stackedviolin(adata, markers_dict, cluster_header, 
                    dendrogram=True, use_raw=False,
                    gene_symbols='gene_symbol',
                    save="svg", output_folder=output_folder,
                    outputfilename_suffix=outputfilename_prefix)

ns.pl.matrixplot(adata, markers_dict, cluster_header, 
                 dendrogram=True, use_raw=False,
                 gene_symbols='gene_symbol',
                 save="svg", output_folder=output_folder,
                 outputfilename_suffix=outputfilename_prefix)
```

## Key Points

| Component | Value | Why |
|-----------|-------|-----|
| adata.var_names | ENSG IDs | Keep as is - scanpy needs these to find genes |
| adata.var['gene_symbol'] | Gene symbols | ADD this - scanpy uses for display |
| markers_dict | ENSG IDs | Use NSForest_markers (not gene_names) |
| gene_symbols parameter | 'gene_symbol' | Tells scanpy which column has display names |

## What NOT To Do

```python
# DON'T create gene_names column
results_to_plot['gene_names'] = [...]  # Wrong

# DON'T use symbols in markers_dict
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["gene_names"]))  # Wrong

# DON'T forget gene_symbols parameter
ns.pl.dotplot(adata, markers_dict, cluster_header)  # Shows ENSG IDs
```

## Troubleshooting

**Error: KeyError: "Could not find keys ['CD3D', ...] in adata.var_names"**

Solution: You're using gene symbols in markers_dict. Use ENSG IDs instead:
```python
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))  # ENSG IDs
```

**Plot shows ENSG IDs instead of gene names**

Solution: Add gene_symbols parameter:
```python
ns.pl.dotplot(adata, markers_dict, cluster_header, 
              gene_symbols='gene_symbol')  # Add this parameter
```
