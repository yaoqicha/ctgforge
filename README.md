# ctgforge

**Turn ClinicalTrials.gov v2 studies into analytics-ready DataFrames and knowledge graphs.**

ClinicalTrials.gov provides one of the most comprehensive public registries of clinical trials — but its modern v2 API exposes data in a deeply nested, regulatory-oriented structure that is difficult to query, flatten, and analyze.

`ctgforge` bridges that gap.

It gives researchers and developers a clean, opinionated Python toolkit to:

- 🔍 **Query** ClinicalTrials.gov v2 with a safe, composable DSL
- 🧱 **Flatten** layered study records into canonical trial objects
- 📊 **Export** trials as pandas DataFrames for analysis
- 🕸️ **Generate** property-graph tables (nodes & edges) for downstream Knowledge-Graph/AI workflows
- 🧾 **Preserve provenance**, so every flattened field can be traced back to its original CTG module

`ctgforge` is designed for people who *actually work* with clinical trials data — not just for making API calls, but for **analysis, modeling, and knowledge integration**.

## Why ctgforge?

ClinicalTrials.gov is a **regulatory registry**, not an analytics database.

That means:

- deeply nested JSON (`sections → modules → items`)
- verbose, evolving schemas
- query syntax that is powerful but easy to misuse

Most users end up writing custom scripts to:

- flatten the same fields
- reconcile the same inconsistencies
- rebuild the same tables and graphs

**ctgforge makes those decisions once — and makes them explicit.**

## Quick taste

```python
from ctgforge import CTG, F
from ctgforge.flatten import flatten_core
from ctgforge.export import to_dataframe, to_property_graph

client = CTG()

q = (
    F.sponsor.eq("pfizer") &
    F.condition.contains("lung cancer") &
    F.phase.in_(["PHASE3", "PHASE4"]) &
    F.status.in_(["RECRUITING", "COMPLETED"])
)

count = client.count(q)
raw = client.search(q, offset=20, limit=100)
trials = [flatten_core(r) for r in raw]

df = to_dataframe(trials)
nodes, edges = to_property_graph(trials)
```

At this point you have:

- a wide trial table for analytics
- node/edge tables ready for graph import
- a stable, inspectable data model

### How to query

- **Single Query**: `F.{field}.{operator}({value})`
- **Available Fields**: `sponsor`, `condition`, `intervention`, `phase`, `status`, `title`
- **Available Operators**: `eq`, `contains`, `in_`

Logical operators `&` `|` `!` can be used to combine multiple queries. However, the `|` (OR) operator across different fields such as `F.condition.eq("diabetes") | F.sponsor.eq("Acme Pharma")` will raise an error.

You may add extra criteria to `count` or `search`, such as  
`client.count(q, extra={"query.term": "AREA[LastUpdatePostDate]RANGE[2025-01-01,MAX]"})`

For the format of raw criteria, please refer to [ClinicalTrials.gov API Specification](https://clinicaltrials.gov/data-api/api).

## Who this is for

- Clinical researchers working with trial registries
- Bioinformatics and healthcare data engineers
- Data scientists building trial-level datasets
- Teams constructing knowledge graphs or RAG systems from clinical trials

If you just want raw API responses, you don’t need `ctgforge`.  
If you want usable trial data, you probably do.

## Project status

`ctgforge` is under active development and currently in alpha.  
The public API is intentionally small and designed to evolve carefully.
