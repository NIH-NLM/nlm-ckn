"""
Map ENSG IDs to Gene Symbols using cell-kn gene_mapping.csv

This script provides utilities to convert Ensembl gene IDs (ENSG) to 
human-readable gene symbols using the NIH NLM cell-kn gene mapping file.

Repository: https://github.com/NIH-NLM/cell-kn
Mapping file: data/biomart/gene_mapping.csv

Quick Start (NSForest Workflow)
--------------------------------
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

# Load mapping (cached for speed)
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)

# Add gene symbols to adata for plotting
adata.var['gene_symbol'] = [ensg_to_symbol.get(gene, gene) for gene in adata.var_names]

# Create markers_dict with ENSG IDs (matches adata.var_names)
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))

# Plot with gene symbols displayed
import nsforest as ns
ns.pl.dotplot(adata, markers_dict, cluster_header, 
              dendrogram=True, gene_symbols='gene_symbol')

Author: NIH NLM cell-kn
License: MIT (or match repository license)
"""

import pandas as pd
import os
from typing import List, Dict, Union

# =============================================================================
# Configuration
# =============================================================================

GENE_MAPPING_URL = "https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/data/biomart/gene_mapping.csv"
DEFAULT_CACHE_FILE = "gene_mapping.csv"

# =============================================================================
# Core Functions
# =============================================================================

def load_gene_mapping(cache_file: str = DEFAULT_CACHE_FILE, 
                     use_cache: bool = True) -> pd.DataFrame:
    """
    Load gene mapping file from GitHub or local cache.
    
    Parameters
    ----------
    cache_file : str
        Local filename to cache the mapping file
    use_cache : bool
        If True, use cached file if it exists; if False, always download fresh
    
    Returns
    -------
    pd.DataFrame
        Gene mapping dataframe with columns: ensembl_gene_id, external_gene_name
    
    Examples
    --------
    >>> gene_mapping = load_gene_mapping()
    >>> print(gene_mapping.head())
    """
    if use_cache and os.path.exists(cache_file):
        print(f"Loading gene mapping from {cache_file}")
        return pd.read_csv(cache_file)
    else:
        print(f"Downloading gene mapping from GitHub...")
        gene_mapping = pd.read_csv(GENE_MAPPING_URL)
        if use_cache:
            gene_mapping.to_csv(cache_file, index=False)
            print(f"Cached to {cache_file}")
        return gene_mapping


def create_mapping_dict(gene_mapping: pd.DataFrame) -> Dict[str, str]:
    """
    Create ENSG ID to gene symbol mapping dictionary.
    
    Parameters
    ----------
    gene_mapping : pd.DataFrame
        Gene mapping dataframe
    
    Returns
    -------
    dict
        Dictionary mapping ensembl_gene_id to external_gene_name
    
    Examples
    --------
    >>> gene_mapping = load_gene_mapping()
    >>> ensg_to_symbol = create_mapping_dict(gene_mapping)
    >>> print(ensg_to_symbol['ENSG00000167286'])
    'CD3D'
    """
    return dict(zip(gene_mapping['ensembl_gene_id'], 
                   gene_mapping['external_gene_name']))


def map_genes(gene_list: List[str], 
             mapping_dict: Dict[str, str]) -> List[str]:
    """
    Map a list of ENSG IDs to gene symbols.
    
    Parameters
    ----------
    gene_list : list
        List of gene identifiers (ENSG IDs or symbols)
    mapping_dict : dict
        Dictionary mapping ENSG IDs to symbols
    
    Returns
    -------
    list
        List of gene symbols (keeps original if mapping not found)
    
    Examples
    --------
    >>> ensg_list = ['ENSG00000167286', 'ENSG00000010610']
    >>> mapped = map_genes(ensg_list, ensg_to_symbol)
    >>> print(mapped)
    ['CD3D', 'CD4']
    """
    return [mapping_dict.get(gene, gene) for gene in gene_list]


def map_dataframe_column(df: pd.DataFrame, 
                        column: str,
                        mapping_dict: Dict[str, str],
                        new_column: str = None) -> pd.DataFrame:
    """
    Map ENSG IDs in a dataframe column to gene symbols.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing gene lists
    column : str
        Column name containing lists of ENSG IDs
    mapping_dict : dict
        Dictionary mapping ENSG IDs to symbols
    new_column : str, optional
        Name for new column with mapped genes (default: column + '_symbols')
    
    Returns
    -------
    pd.DataFrame
        Dataframe with new column containing mapped gene symbols
    
    Examples
    --------
    >>> results['gene_names'] = map_dataframe_column(
    ...     results, 'NSForest_markers', ensg_to_symbol, 'gene_names')
    """
    if new_column is None:
        new_column = f"{column}_symbols"
    
    # Fast list comprehension (5-10x faster than apply)
    df[new_column] = [
        [mapping_dict.get(gene, gene) for gene in genes]
        for genes in df[column]
    ]
    
    return df


# =============================================================================
# Quick Start Function
# =============================================================================

def quick_map(gene_list_or_df: Union[List[str], pd.DataFrame],
             column: str = None,
             cache_file: str = DEFAULT_CACHE_FILE) -> Union[List[str], pd.DataFrame]:
    """
    Quick one-function mapping for common use cases.
    
    Parameters
    ----------
    gene_list_or_df : list or pd.DataFrame
        Either a list of ENSG IDs or a dataframe with a column of gene lists
    column : str, optional
        If df provided, the column name containing gene lists
    cache_file : str
        Local cache filename
    
    Returns
    -------
    list or pd.DataFrame
        Mapped genes as list, or dataframe with new mapped column
    
    Examples
    --------
    # Map a single list
    >>> genes = ['ENSG00000167286', 'ENSG00000010610']
    >>> mapped = quick_map(genes)
    >>> print(mapped)
    ['CD3D', 'CD4']
    
    # Map a dataframe column
    >>> df = quick_map(results_df, column='NSForest_markers')
    """
    # Load mapping
    gene_mapping = load_gene_mapping(cache_file=cache_file)
    ensg_to_symbol = create_mapping_dict(gene_mapping)
    
    # Map based on input type
    if isinstance(gene_list_or_df, list):
        return map_genes(gene_list_or_df, ensg_to_symbol)
    elif isinstance(gene_list_or_df, pd.DataFrame):
        if column is None:
            raise ValueError("Must specify column name for dataframe input")
        return map_dataframe_column(gene_list_or_df, column, ensg_to_symbol)
    else:
        raise TypeError("Input must be list or pd.DataFrame")


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    
    print("="*80)
    print("EXAMPLE 1: Map a single list of genes")
    print("="*80)
    
    # Load mapping once
    gene_mapping = load_gene_mapping()
    ensg_to_symbol = create_mapping_dict(gene_mapping)
    
    # Map some genes
    test_genes = ['ENSG00000167286', 'ENSG00000010610', 'ENSG00000153563']
    mapped_genes = map_genes(test_genes, ensg_to_symbol)
    
    print("\nInput ENSG IDs:")
    for gene in test_genes:
        print(f"  {gene}")
    
    print("\nMapped to symbols:")
    for orig, mapped in zip(test_genes, mapped_genes):
        print(f"  {orig} -> {mapped}")
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Map genes in a dataframe (NSForest results)")
    print("="*80)
    
    # Example dataframe structure
    example_df = pd.DataFrame({
        'clusterName': ['CD4+ T cells', 'CD8+ T cells', 'B cells'],
        'NSForest_markers': [
            ['ENSG00000167286', 'ENSG00000010610'],
            ['ENSG00000167286', 'ENSG00000153563'],
            ['ENSG00000156738', 'ENSG00000198851']
        ]
    })
    
    print("\nBefore mapping:")
    print(example_df)
    
    # Map using fast method
    example_df = map_dataframe_column(example_df, 'NSForest_markers', 
                                      ensg_to_symbol, 'gene_names')
    
    print("\nAfter mapping:")
    print(example_df[['clusterName', 'gene_names']])
    
    # Create markers_dict for plotting
    markers_dict = dict(zip(example_df['clusterName'], 
                           example_df['gene_names']))
    
    print("\nmarkers_dict for plotting:")
    for cluster, genes in markers_dict.items():
        print(f"  {cluster}: {genes}")
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Quick one-liner")
    print("="*80)
    
    # Map a list in one line
    quick_mapped = quick_map(['ENSG00000167286', 'ENSG00000010610'])
    print(f"\nQuick map result: {quick_mapped}")


# =============================================================================
# For NSForest Users - Complete Workflow
# =============================================================================

"""
COMPLETE WORKFLOW FOR NSFOREST RESULTS
---------------------------------------

# 0. Download utility (one-time)
import urllib.request
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/utils/gene_mapping_utils.py",
    "gene_mapping_utils.py"
)

# 1. Import utilities
import pandas as pd
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

# 2. Load gene mapping (cached for speed)
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)
print(f"Loaded {len(gene_mapping)} gene mappings")

# 3. Add gene symbols to adata
# This allows scanpy to display readable gene names on plots
adata.var['gene_symbol'] = [ensg_to_symbol.get(gene, gene) for gene in adata.var_names]
print(f"Added gene symbols to adata.var['gene_symbol']")

# 4. Create markers_dict with ENSG IDs (matches adata.var_names)
# IMPORTANT: Use NSForest_markers (ENSG IDs), NOT mapped gene names
markers_dict = dict(zip(results_to_plot["clusterName"], 
                       results_to_plot["NSForest_markers"]))

print(f"markers_dict created with {len(markers_dict)} clusters")

# 5. Plot with readable gene symbols displayed
# The gene_symbols='gene_symbol' parameter tells scanpy to display
# gene symbols on the plot while using ENSG IDs to look up the data
import nsforest as ns

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
"""
