# NLM Cell Knowledge Network MVP

The [National Library of Medicine (NLM) Cell Knowledge Network](http://cell-kn-mvp.org/) is a knowledgebase about cell characteristics (phenotypes) emerging from single cell technologies, integrated with other sources of trusted knowledge, sourced from:

* Validated data processing and analysis pipelines
* Reference ontologies
* NCBI and other information resources
* LLM-based text mining

A knowledge graph is produced from triple assertions (subject-predicate-object) corresponding to biomedical entities (nodes) and their relations (edges), and links experimental data to the reference Cell Ontology as evidence in support of assertions. The graph integrates single cell genomics experimental data with other information sources about cells, tissues, biomarkers, pathways, drugs, diseases.

This application creates a knowledge network encapsulating the latest knowledge on cells, the evidence primarily coming from single cell RNA-sequencing experiments, including but not limited single nucleus as well as single cell RNA-sequencing experiments, spatial cell RNA-sequencing experiments.  The majority of these data and those stored within many repositories, notably the chan-zuckerburg [cellxgene](https://cellxgene.cziscience.com/).  Many of these data the foundations for numerous cell atlases.

The NLM Cell Knowledge Network aims to connect this experiment data and augment it with marker data computationally derived from exeuction of the [NSForest](https://github.com/JCVenterInstitute/NSForest/tree/master) program which calculates both the necessary and sufficient genes that when present define the cell cluster, resolved to a cell ontological type using semantic terms updated and maintained at the [Cell Ontology](https://www.ebi.ac.uk/ols4/ontologies/cl) 

## NLM Cell KN Infrastructure Architecture

![](https://github.com/NIH-NLM/cell-kn-mvp/blob/main/docs/_static/NLM_Cell_KN_Infrastructure.png)

## Repositories of Interest

* [NLM Cell KN Extract Transform Load Ontologies](https://github.com/NIH-NLM/cell-kn-mvp-etl-ontologies#README)

* [NLM Cell KN Extract Transform Load Results](https://github.com/NIH-NLM/cell-kn-mvp-etl-results#README)

* [NLM Cell KN User Interface](https://github.com/NIH-NLM/cell-kn-mvp-ui#README)

## Navigating NLM Cell KN MVP

![NLM Cell KN MVP Search](docs/_static/NLM_Cell_KN_MVP_Search_Window.png)

![NLM Cell KN MVP Browse](docs/_static/NLM_Cell_KN_MVP_Browse_Database.png)

![NLM Cell KN MVP Explore](docs/_static/NLM_Cell_KN_MVP_Explore_the_Tree.png)

![NLM Cell KN MVP Gene Symbol KCKN3](docs/_static/NLM_Cell_KN_MVP_Gene_Symbol_KCKN3.png)

![NLM Cell KN MVP Inspect](docs/_static/NLM_Cell_KN_MVP_Inspect_Data_Collections.png)

![NLM Cell KN MVP Schema](docs/_static/NLM_Cell_KN_MVP_Schema.png)

![NLM Cell KN MVP About](docs/_static/NLM_Cell_KN_MVP_About.png)

## Additional repositories

* [NLM Cell KN SCsilhouette Score Package](https://github.com/NIH-NLM/scsilhouette#README)

  [SCsilhouette Score Read the Docs](https://nih-nlm.github.io/scsilhouette/)
  
* [NLM Cell KN Silhouette Score Nextflow Workflow](https://github.com/NIH-NLM/scsilhouette-nf#README))

* [NSForest Package](https://github.com/JCVenterInstitute/NSForest#README)

  [NSForest Read the Docs](https://nsforest.readthedocs.io/en/latest/)

* [NLM Cell KN NS Forest Nextflow Workflow](https://github.com/NIH-NLM/nsforest-nf#README)

