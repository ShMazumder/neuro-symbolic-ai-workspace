# References & Resources

---

## Data Sources

| Source | URL | Description | Access |
|--------|-----|-------------|--------|
| The Daily Star (RSS) | `https://www.thedailystar.net/frontpage/rss.xml` | Primary news feed — English, Bangladesh | Free (RSS) |
| The Daily Star (Category RSS) | `https://www.thedailystar.net/rss` | All category feeds | Free |
| GDELT Project | `https://www.gdeltproject.org/` | Global event database, CAMEO-coded, auto-extracted | Free API |
| ACLED | `https://acleddata.com/` | Armed Conflict Location & Event Data, human-coded | Free (academic) |
| CAMEO Codebook | `https://parusanalytics.com/eventdata/data.dir/cameo.html` | Official CAMEO event coding manual | Free |
| CAMEO GitHub | `https://github.com/openeventdata/CAMEO` | Machine-readable CAMEO codes | Free |
| NewsData.io | `https://newsdata.io/` | Third-party news API (can filter by thedailystar.net) | Freemium |

---

## Key Papers

### Neuro-Symbolic AI
- Hitzler, P. et al. (2022). "Neuro-Symbolic Artificial Intelligence: The State of the Art." *IOS Press.*
- Garcez, A. & Lamb, L. (2023). "Neurosymbolic AI: The 3rd Wave." *Artificial Intelligence Review.*
- Hamilton, W. (2020). "Graph Representation Learning." *Morgan & Claypool.*

### Event Extraction & Conflict Coding
- Schrodt, P. (2012). "CAMEO: Conflict and Mediation Event Observations Event and Actor Codebook."
- Halterman, A. et al. (2023). "Mordecai 3: A Neural Geoparser and Event Geocoder." *J. Open Source Software.*
- Radford, B. (2021). "Automated Conflict Event Coding from Political Text." *Political Analysis.*

### Knowledge Graphs + NLP
- Pan, J. et al. (2024). "Unifying Large Language Models and Knowledge Graphs: A Roadmap." *IEEE TKDE.*
- Rossi, A. et al. (2021). "Knowledge Graph Embedding for Link Prediction: A Comparative Analysis." *ACM TKDD.*

### BlazeGraph / RDF
- Thompson, B. et al. (2014). "Blazegraph/Wikidata Query Service." *ISWC.*
- W3C. (2014). "RDF 1.1 Primer." `https://www.w3.org/TR/rdf11-primer/`
- W3C. (2013). "SPARQL 1.1 Query Language." `https://www.w3.org/TR/sparql11-query/`

### Bangladesh Conflict Context
- Ain o Salish Kendra — Annual human rights reports: `https://askbd.org/`
- Odhikar — Human rights monitoring: `https://odhikar.org/`
- Bangladesh Peace Observatory (if available)

---

## Tools & Libraries

| Category | Tool | URL |
|----------|------|-----|
| NLP | spaCy | `https://spacy.io/` |
| NLP | HuggingFace Transformers | `https://huggingface.co/docs/transformers/` |
| KG | RDFLib | `https://rdflib.readthedocs.io/` |
| KG | BlazeGraph | `https://blazegraph.com/` |
| KG | SPARQLWrapper | `https://sparqlwrapper.readthedocs.io/` |
| GNN | PyTorch Geometric | `https://pyg.org/` |
| GNN | PyKEEN | `https://pykeen.readthedocs.io/` |
| Ontology | Protégé | `https://protege.stanford.edu/` |
| LLM | LangChain | `https://python.langchain.com/` |
| LLM | Ollama | `https://ollama.com/` |
| Viz | Streamlit | `https://streamlit.io/` |
| Viz | Gephi | `https://gephi.org/` |

---

## Existing Open-Source Projects (Reference)

| Project | URL | Relevance |
|---------|-----|-----------|
| PETRARCH2 | `https://github.com/openeventdata/petrarch2` | CAMEO event coder (rule-based, older) |
| Mordecai3 | `https://github.com/ahalterman/mordecai3` | Neural geoparser for conflict events |
| bdnews-scraper | `https://github.com/topics/bangladesh-news` | Community scrapers for BD news |
| GDELT Analysis | `https://github.com/linwoodc3/gdeltPyR` | Python wrapper for GDELT API |
