# **Professor Presentation Handnote**

## **Neuro-Symbolic AI for Violence Analysis in Bangladeshi News**

Research project

AI + Knowledge Graphs

Bangladesh-focused

**Repository:** [github.com/ShMazumder/neuro-symbolic-ai-workspace](https://github.com/ShMazumder/neuro-symbolic-ai-workspace?utm_source=chatgpt.com)

### **1. Project Overview**

This project explores how **Neuro-Symbolic Artificial Intelligence** can be used to automatically identify, classify, represent, and analyse violence-related events reported in Bangladeshi online news.

The central idea is to combine two AI approaches:

- **Neural AI:** Uses NLP and deep learning to understand unstructured news articles and extract entities, events, and relationships.
- **Symbolic AI:** Uses formal ontologies, knowledge graphs, and logical reasoning to represent facts and identify meaningful relationships between events.

Rather than relying entirely on a language model or a conventional machine-learning classifier, the proposed system combines data-driven learning with structured knowledge and reasoning.

### **2. Research Problem**

Traditional NLP systems can identify keywords and classify news articles, but they often struggle with:

- Understanding relationships between multiple events.
- Identifying actors, victims, locations, and event types.
- Connecting related incidents across different news reports.
- Reasoning over historical events and detecting potential patterns.
- Providing explainable conclusions backed by structured evidence.

**Research question:** Can a hybrid neuro-symbolic framework improve the extraction, representation, analysis, and explainability of violence-related events in Bangladeshi news?

### **3. Proposed Solution**

The project uses news articles from **The Daily Star** as its primary source and integrates the CAMEO event-coding framework to structure violence-related events.

[Bridging Mind and Machine: The Promise of Neuro-Symbolic AI in Healthcare](https://images.openai.com/static-rsc-4/GKdh335m-uf1As1QlStnpZ4lrBc70vKtjz417ORkq2AXdWtr7qareHmhgBo0BfEOEGDFIU9KnaWtP_YJtg3u83KMyAaclN2BarsLB3-bwIYktYP-hcFX20-Pth-MDhOeS5N0nV-wbzc2t_SIMVojZoRpl4S6Y6dUcA4UarodMGY?purpose=inline)

[linkedin.com](https://www.linkedin.com/pulse/bridging-mind-machine-promise-neuro-symbolic-ai-susith-athukorala-j2hdc?utm_source=chatgpt.com)

The proposed pipeline consists of:

1. **News Collection:** Collect articles through RSS feeds and web scraping.
2. **NLP Processing:** Extract named entities, event triggers, actors, and relevant information.
3. **Event Classification:** Categorise events using CAMEO event codes.
4. **Knowledge Graph Construction:** Represent events and relationships as RDF triples.
5. **Neural Learning:** Apply knowledge graph embeddings, graph neural networks, and deep learning.
6. **Symbolic Reasoning:** Use ontology-based relationships and logical rules to support structured analysis.
7. **Analysis & Visualisation:** Provide graph queries, natural-language access, and an interactive dashboard.

### **4. Technologies and Research Components**

| Component                | Technology / Method                   |
| ------------------------ | ------------------------------------- |
| Programming              | Python                                |
| NLP                      | NER, event extraction, classification |
| Event ontology           | CAMEO, OWL                            |
| Knowledge representation | RDF, SPARQL                           |
| Graph database           | BlazeGraph                            |
| Knowledge embeddings     | TransE, RotatE                        |
| Graph neural networks    | R-GCN / relational GNN                |
| Deep learning            | BiLSTM                                |
| Reasoning                | OWL / symbolic rules                  |
| API and interface        | FastAPI, Streamlit                    |
| Evaluation               | GDELT, ACLED, human annotation        |

### **5. Preliminary Experimental Findings**

The repository includes an experimental report dated 21 October 2026. Some notable reported results are:

# **80.7%**

**Hybrid accuracy**

High-violence binary classification

# **76.2%**

**Hybrid precision**

High-violence detection

# **10.1%**

**False-positive rate**

Hybrid model

# **97%**

**Provenance coverage**

Audited prediction explanations

The reported ablation study compares four approaches:

- Zero-shot NLI transformer.
- Dense neural model.
- Symbolic-only reasoning.
- Proposed hybrid neuro-symbolic approach.

The hybrid approach reportedly achieved 80.7% binary accuracy, compared with 52.7% for the dense neural baseline. Its false-positive rate was 10.1%, compared with 56.6% for that baseline. These results suggest that symbolic constraints may help reduce false alarms.

**Important research limitation:** External validation is not yet strong enough to claim a production-ready conflict prediction system. The report identifies 39% detection recall against ACLED, 60% CAMEO group agreement among matched events, and 0% exact CAMEO sub-code accuracy. These limitations are important research opportunities rather than results to conceal.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



### **6. Potential Research Contributions**

The project can be developed into several research contributions:

1. **Bangladesh-specific event ontology:** Extending CAMEO to represent local political, social, and violence-related contexts.
2. **Hybrid reasoning framework:** Combining neural predictions with symbolic constraints to improve classification reliability.
3. **Explainable event intelligence:** Linking each prediction to its original news article, sentence, entities, and activated reasoning rules.
4. **Conflict pattern analysis:** Identifying temporal and geographical patterns in violence-related incidents.
5. **Cross-source validation:** Evaluating news-derived events against independent conflict datasets such as ACLED and GDELT.

### **7. Repository Structure**

The repository is organised as a research and implementation workspace:

| Directory          | Purpose                              |
| ------------------ | ------------------------------------ |
| `scraper/`         | News collection                      |
| `nlp/`             | Text processing and event extraction |
| `ontology/`        | CAMEO ontology and extensions        |
| `knowledge_graph/` | RDF and graph operations             |
| `neurosymbolic/`   | Neural and symbolic reasoning        |
| `evaluation/`      | Experiments and benchmarks           |
| `api/`             | Graph-RAG and query interface        |
| `dashboard/`       | Interactive visualisation            |
| `notebooks/`       | Research experiments                 |
| `docs/`            | Research documentation               |
| `tests/`           | Software tests                       |

The repository also contains modular research notebooks, an end-to-end pipeline demonstration, technical documentation, and an experiment report.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

ShMazumder/neuro-symbolic-ai-workspace · GitHub



### **8. Suggested 1-Minute Presentation Script**

You can explain the project to your professor in the following way:

> Sir, I would like to introduce a research project I have been developing called **NeuroSym-BD: Neuro-Symbolic AI for Violence Analysis in Bangladeshi News**.
>
> The primary objective is to explore how neural AI and symbolic AI can work together to understand and analyse real-world events from news articles.
>
> For example, if a newspaper reports that protesters clashed with police in a particular district, the system attempts to identify the actors, classify the event, determine its location and date, and store the information in a structured knowledge graph.
>
> We use NLP and deep-learning techniques for information extraction, the CAMEO ontology for event classification, RDF knowledge graphs for structured representation, and graph neural networks alongside symbolic reasoning for analysis.
>
> I have organised the project into a modular research workspace, including the implementation pipeline, experimental notebooks, evaluation benchmarks, and technical documentation.
>
> My broader research interest is to investigate whether combining neural learning with symbolic reasoning can improve the reliability, explainability, and contextual understanding of AI systems.

### **9. What I Would Like to Discuss with You**

- Is the proposed research direction sufficiently novel for a publishable research contribution?
- Is the neuro-symbolic integration method appropriate, or should we investigate alternative architectures?
- How can we strengthen the experimental design and external validation?
- Could this be developed into a longer-term research collaboration or publication?

### **10. Recommended Repository Tour**

If the professor wants to inspect the actual work, show these in order:

1. [README – Project overview](https://github.com/ShMazumder/neuro-symbolic-ai-workspace?utm_source=chatgpt.com)
2. [System architecture](https://github.com/ShMazumder/neuro-symbolic-ai-workspace/blob/main/docs/02_ARCHITECTURE.md?utm_source=chatgpt.com)
3. [CAMEO ontology extension](https://github.com/ShMazumder/neuro-symbolic-ai-workspace/blob/main/docs/04_CAMEO_EXTENSION.md?utm_source=chatgpt.com)
4. [Research notebooks](https://github.com/ShMazumder/neuro-symbolic-ai-workspace/tree/main/notebooks?utm_source=chatgpt.com)
5. [Experimental results](https://github.com/ShMazumder/neuro-symbolic-ai-workspace/blob/main/docs/07_EXPERIMENT_REPORT.md?utm_source=chatgpt.com)
6. [Research opportunities](https://github.com/ShMazumder/neuro-symbolic-ai-workspace/blob/main/docs/08_RESEARCH_OPPORTUNITIES.md?utm_source=chatgpt.com)

**My recommendation:** Present this as an ongoing research prototype with preliminary experimental evidence, not as a finished or validated violence-prediction product. In particular, be transparent about the ACLED validation limitations and the relatively low multiclass CAMEO accuracy.

*Note: I reviewed the public repository README, architecture documentation and experiment report. The reported experimental metrics are taken from the repository; I have not independently rerun the experiments or audited every implementation module.*

The most important message to leave with the professor is:

**"I am interested in moving beyond conventional black-box AI towards systems that can learn from data, reason with structured knowledge, and explain why they make a particular decision."**
