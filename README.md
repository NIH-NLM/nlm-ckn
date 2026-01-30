# NLM Cell Knowledge Network

The __National Library of Medicine (NLM) Cell Knowledge Network__ [`http://cell-kn-mvp.org/`](http://cell-kn-mvp.org/) is a knowledgebase about cell characteristics (phenotypes) emerging from single cell technologies, integrated with other sources of trusted knowledge, sourced from:

* Validated data processing and analysis pipelines
* Reference ontologies
* NCBI and other information resources
* LLM-based text mining

A knowledge graph is produced from triple assertions (subject-predicate-object) corresponding to biomedical entities (nodes) and their relations (edges), and links experimental data to the reference Cell Ontology as evidence in support of assertions. The graph integrates single cell genomics experimental data with other information sources about cells, tissues, biomarkers, pathways, drugs, diseases.

This application creates a knowledge network encapsulating the latest knowledge on cells, the evidence primarily coming from single cell genomics experiments, including but not limited single nucleus as well as single cell RNA-sequencing experiments, spatial transcriptomics experiments.  The majority of these data and those stored within many data repositories, notably the Chan-Zuckerburg [CELLxGENE](https://cellxgene.cziscience.com/).  Many of these data form the foundations for numerous cell atlases.

The NLM Cell Knowledge Network aims to connect these experimental data augmented with characterizing marker genes computationally derived from the [NS-Forest](https://github.com/JCVenterInstitute/NSForest/tree/master) machine learning method, which identifies the necessary and sufficient marker genes that define the data-driven cell type cluster, resolved to a cell ontological type using semantic terms updated and maintained at the [Cell Ontology](https://www.ebi.ac.uk/ols4/ontologies/cl).

__*This resource is under active development. To contribute, please open an [issue](https://github.com/NIH-NLM/cell-kn/issues) on this Github repository.*__

## NLM Cell KN Infrastructure Architecture

<img src="docs/_static/NLM_Cell_KN_Infrastructure.png" width="750" />

## Repositories of Interest

* [NLM Cell KN Schema](https://github.com/NIH-NLM/cell-kn-schema#README)

* [NLM Cell KN Extract Transform Load Ontologies](https://github.com/NIH-NLM/cell-kn-mvp-etl-ontologies#README)

* [NLM Cell KN Extract Transform Load Results](https://github.com/NIH-NLM/cell-kn-mvp-etl-results#README)

* [NLM Cell KN User Interface](https://github.com/NIH-NLM/cell-kn-mvp-ui#README)

## Navigating NLM Cell KN

### Search Landing Page - A good place to start

Here you can enter any term within any of the data collections.

<img src="docs/_static/NLM_Cell_KN_MVP_Search_Window.png" width="750" />

### Browse the Database - Another place to begin

Here with this Sunburst Graph, you can navigate and browse by organism, tissue and cell type.

<img src="docs/_static/NLM_Cell_KN_MVP_Browse_Database.png" width="750" />

### Alternative view of the Sunburst Graph as a Tree

An alternative view of the sunburst graph, you can explore the tree - same information - different navigational style.

<img src="docs/_static/NLM_Cell_KN_MVP_Explore_the_Tree.png" width="750" />

### Landing page for a Gene Symbol

When you get to a gene of interest, or an item of interest, you can further explore the graphs and the content, with links out to source information (e.g. NCBI Gene).

<img src="docs/_static/NLM_Cell_KN_MVP_Gene_Symbol_KCKN3.png" width="750" />

### Inspect Data Collections

Exploring can also begin with the available data collections.

<img src="docs/_static/NLM_Cell_KN_MVP_Inspect_Data_Collections.png" width="750" />

### The NLM Cell Schema

You can see the relationships held in the graph by looking at the static schema.  

<img src="docs/_static/NLM_Cell_KN_MVP_Schema.png" width="750" />

### About the NLM Cell KN

<img src="docs/_static/NLM_Cell_KN_MVP_About.png" width="750" />

## Additional repositories of interest

### The Single Cell Silhouette Python Package

These repositories: a python package and its partner Nextflow workflow are used to assess the quality of the dataset clusters. It does so by creating an interactive html chart using plotly to allow the team to explore the author submitted clusters and others to determine inclusion criteria for the repository.

* [NLM Cell KN SCsilhouette Score Package](https://github.com/NIH-NLM/scsilhouette#README)
* [NLM Cell KN Silhouette Score Nextflow Workflow](https://github.com/NIH-NLM/scsilhouette-nf#README)

### The NS-Forest Python Package

These repositories: a python package created at the JCVenter Institute and its partner Nextflow workflow are used to identify cell type characterizing marker genes and calculate associated F-beta score.   The F-beta score is used as a confidence metric for consideration as well as understanding the robustness of the markers.

* [NS-Forest Package](https://github.com/JCVenterInstitute/NSForest#README)
* [NLM Cell KN NS Forest Nextflow Workflow](https://github.com/NIH-NLM/nsforest-nf#README)

