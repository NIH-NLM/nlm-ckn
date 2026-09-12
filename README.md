# NLM Cell Knowledge Network (NLM-CKN)
[<img src="docs/_static/nlm-ckn-logo-light-sm.png" width="150"  align=left>](https://nlm-ckn.org/)

The __National Library of Medicine (NLM) Cell Knowledge Network (**NLM-CKN**)__ is a knowledgebase focused on cell characteristics (phenotypes) derived from single-cell technologies. It integrates this information with data from reference ontologies, NCBI resources, and text mining efforts.

The network is structured as a knowledge graph of biomedical entities (nodes) and their relationships (edges). This graph links experimental single-cell genomics data to the reference Cell Ontology, providing evidence for assertions and integrating information about cells, tissues, biomarkers, pathways, drugs, and diseases.

Use the search bar above to find and explore entities within this network. You can add items to your graph or navigate to their specific pages.

**Production Data**
A knowledge graph is produced from triple assertions (subject-predicate-object) corresponding to biomedical entities (nodes) and their relations (edges), and links experimental data to the reference Cell Ontology as evidence in support of assertions. The graph integrates single cell genomics experimental data with other information sources about cells, tissues, biomarkers, pathways, drugs, diseases.

This application creates a knowledge network encapsulating the latest knowledge on cells, the evidence primarily coming from single cell genomics experiments, including but not limited single nucleus as well as single cell RNA-sequencing experiments, spatial transcriptomics experiments.  The majority of these data and those stored within many data repositories, notably the Chan-Zuckerburg [CELLxGENE](https://cellxgene.cziscience.com/).  Many of these data form the foundations for numerous cell atlases.

The NLM-CKN aims to connect these experimental data augmented with characterizing marker genes computationally derived from the [NS-Forest](https://github.com/JCVenterInstitute/NSForest/tree/master) machine learning method, which identifies the necessary and sufficient marker genes that define the data-driven cell type cluster, resolved to a cell ontological type using semantic terms updated and maintained at the [Cell Ontology](https://www.ebi.ac.uk/ols4/ontologies/cl).

__*This resource is under active development. To contribute, please open an [issue](https://github.com/NIH-NLM/nlm-ckn/issues) on this Github repository.*__

## NLM-CKN Infrastructure Architecture

### Data Harvesting

The [cellxgene-harvester](https://github.com/NIH-NLM/cellxgene-harvester#cellxgene-harvester) harvests, filters, and counts normal cells from the [CellxGene Census](https://chanzuckerberg.github.io/cellxgene-census/) using ontology-based filtering (UBERON tissue, PATO/MONDO disease, HsapDv age). It separates ontology resolution (Steps 0a–0c, run once per scope) from data collection (Steps 1–6), producing a per-organ `homo_sapiens_{organ}_harvester_final.csv` that is the input to the quality-control workflow below:

```
Steps 0a–0c  (resolve — run once per scope, reuse across all datasets)
┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ resolve-uberon   │  │ resolve-disease │  │ resolve-hsapdv   │
│ kidney           │  │ normal          │  │ --min-age 15     │
└────────┬─────────┘  └────────┬────────┘  └─────────┬────────┘
         │                     │                     │
  uberon_kidney.json   disease_normal.json   hsapdv_adult_15.json
         │                     │                     │
         ▼                     ▼                     │
Steps 1–3  (fetch + flatten + enrich CellxGene metadata)
         │                     │                     │
         ▼                     ▼                     │
Step 4   filter-datasets    (uberon + disease JSON)  │
         │                                           │
         ▼                                           ▼
Step 5   count-normal-cells (uberon + disease + hsapdv JSON)
         │
         ▼
Step 6   final-cleanup ──► homo_sapiens_kidney_harvester_final.csv

The same three JSON files are passed to sc-nsforest-qc-nf
for cell-level h5ad filtering (filter_adata, compute_scsilhouette).
```

The same three resolve JSON files are shared with sc-nsforest-qc-nf for cell-level `.h5ad` filtering, giving both pipelines a single, reproducible ontology-scope definition.

### Data Generation and Quality-Control Workflow

The [sc-nsforest-qc-nf](https://github.com/NIH-NLM/sc-nsforest-qc-nf#sc-nsforest-qc-nf) [Nextflow](https://nextflow.io) workflow runs the scsilhouette package and NSForest over each harvested dataset, producing the marker genes, F-scores, and silhouette quality metrics consumed downstream by the ETL pipeline:

```
homo_sapiens_{organ}_harvester_final.csv
uberon_{organ}.json
        │
        ▼
[0] filter_adata         ← tissue (UBERON) + disease (PATO) + age + min cluster size
        │
        ├──────────────────────────────────────────────────┐
        ▼                                                  ▼
[1] dendrogram                                   [10] compute_silhouette
[2] cluster_stats                                [11] viz_summary
        │                                        [11] viz_distribution
        ▼ scatter by cluster                     [11] viz_dotplot
[4] prep_medians ×N                              [12] compute_summary_stats
        │
        ▼ gather
[5] merge_medians
        │
        ▼ scatter by cluster
[6] prep_binary_scores ×N
        │
        ▼ gather
[6] merge_binary_scores
        │
        ├── [7] plot_histograms
        │
        ▼ scatter by cluster
[8] run_nsforest ×N
        │
        ▼ gather
[8] merge_nsforest_results
        │
        ▼
[9] plots
```

The scatter/gather pattern (steps 4–8) parallelizes the computationally intensive median, binary score, and NSForest steps independently across every cluster in every dataset. A dataset with 50 clusters runs 50 parallel jobs at each scatter stage.

### ETL Pipeline

The [NLM-CKN ETL](https://github.com/NIH-NLM/nlm-ckn-etl#README) pipeline produces an ArangoDB archive from single cell genomics results and source ontologies: a Data Processing Pipeline (DataFetcher → DataTransformer → TupleWriters → ResultsGraphBuilder) and an Ontology Processing Pipeline (OntologyDownloader → OntologyGraphBuilder) feed ArangoDB graph storage, from which the InducedSubgraphBuilder selects a relevant subgraph.

<img src="docs/_static/NLM-CKN-ETL.png" width="750" />

### User Interface

The [NLM-CKN User Interface](https://github.com/NIH-NLM/nlm-ckn-ui#README) is a Django and React application that loads a pre-built ArangoDB dataset produced by the ETL pipeline and lets researchers query, visualize, and explore the knowledge graph.

<img src="docs/_static/NLM-CKN-UI.png" width="750" />

## Repositories of Interest

* [NLM-CKN Schema](https://github.com/NIH-NLM/nlm-ckn-schema#README)
  
* [NLM-CKN CellxGene Harvester](https://github.com/NIH-NLM/cellxgene-harvester#cellxgene-harvester)
  This package is used to select cellxgene scRNA-seq and snRNA-seq datasets from cellxgene. Using the cellxgene harvester and obtaining ontologies from the [Ontology Lookup Service]{https://www.ebi.ac.uk/ols4/} 
    * Full API and CLI documentation auto-generated with Sphinx and deployed via GitHub Pages: https://nih-nlm.github.io/cellxgene-harvester/documentation 

* [NLM-CKN scsilhouette Python Package](https://github.com/NIH-NLM/scsilhouette#scsilhouette)
  This package is part of the quality control workflow and together with the NSForest F-scores provides an overview of the single cell clusters used in the knowledgebase.
    * Full CLI documentation auto-generated with Sphinx and deployed via GitHub Pages: [https://nih-nlm.github.io/scsilhouette/](https://nih-nlm.github.io/scsilhouette/)
    * Docker image built and container released with every push via GitHub's container repository [https://github.com/NIH-NLM/scsilhouette/pkgs/container/scsilhouette](https://github.com/NIH-NLM/scsilhouette/pkgs/container/scsilhouette)

* [NLM-CKN sc-nsforest-qc-nf with CLI wrapper to JCVI's NSForest package](https://github.com/NIH-NLM/sc-nsforest-qc-nf#sc-nsforest-qc-nf)
  This [Nextflow](https://nextflow.io) workflow runs the scsilhouette python package via the released container and NSForest via the CLI generating > 50 Artefacts and data for the [NLM-CKN](https://nlm-ckn.org/).
    * Full CLI documentation autogenerated via a python script in the Sphinx style and deployed via GitHub pages [https://nih-nlm.github.io/sc-nsforest-qc-nf/](https://nih-nlm.github.io/sc-nsforest-qc-nf/)
    * Notable is the generation of the combined silhouette bar and whisker plot together with the F-Score bar chart, summarizing the quality assessment for the clusters (cell sets) and cell set data set.
    * Production data and visualizations are published to this repository and are viewable via this repository's GitHub Pages.  This includes all the datasets for each tissue that are:
        * loaded into the [NLM-CKN](https://nlm-ckn.org/)
        * additional visualizations for all datasets for each tissue visible here [https://nih-nlm.github.io/nlm-ckn/](https://nih-nlm.github.io/nlm-ckn/)
        * or you can find the production data directly on GitHub here: [https://github.com/NIH-NLM/nlm-ckn/tree/main/data/prod](https://github.com/NIH-NLM/nlm-ckn/tree/main/data/prod)

* [NLM-CKN Extract, Transform, and Load (ETL)](https://github.com/NIH-NLM/nlm-ckn-etl#README)
  The unified ETL repository, combining the previously separate `nlm-ckn-mvp-etl-ontologies` and `nlm-ckn-mvp-etl-results` repositories (eliminating the need for git submodules and system-scoped JAR dependencies). It provides a Java package for parsing ontology OWL files and loading semantic triples into ArangoDB, and Python modules for creating triples from NSForest results, manual Cell Ontology mappings, external data, and NLP results. The pipeline produces an ArangoDB archive from single cell genomics results and source ontologies.

* [NLM-CKN User Interface](https://github.com/NIH-NLM/nlm-ckn-ui#README)
  The Django and React application serving as the user interface for the NLM-CKN. It lets researchers query, visualize, and explore the graph-based knowledgebase, building and viewing customized subgraphs of relationships between cell types, genes, diseases, and experimental contexts. The app loads a pre-built ArangoDB dataset produced by the `nlm-ckn-etl` pipeline.

## Navigating NLM-CKN 

### Search Landing Page - Best place to Search!

Here you can enter any term, gene, protein, publication, anatomical subunit, etc.
Here you see when you enter `Sikkema`
<img src="docs/_static/NLM-CKN-search-sikkema.png" width="750" />

### Select a result

You can select the `Sikkema publication`
<img src="docs/_static/NLM-CKN-select-sikkema-publication.png" width="750" />

Selecting the publication brings you to a graph that has the all the Cell Sets for this publication. A publication Cell Set Dataset contains all the Cell sets.

You can select one of the cell sets, say neuroendrocrine cell set dataset
<img src="docs/_static/NLM-CKN-select-sikkema-neuroendocrine-cell-set.png" width="750" />

### Cell set Detail

The neuroendrocrine cell set reveals the NS-Forest necessary and sufficient markers (biomarker combination) and the binary genes for this cell set.  This is the quantitative result with a F-Beta score (0.937) showing that there is strong evidence in this experimental cell set dataset for these markers to be able to distinctly identify this cell type.
<img src="docs/_static/NLM-CKN-neuroendocrine-cell-set.png width="750" />

### The NLM Cell Schema

You can see the relationships held in the graph by looking at the static schema.  

<img src="docs/_static/NLM-CKN-schema.png" width="750" />
