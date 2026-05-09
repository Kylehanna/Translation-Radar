# Architecture

## Positioning

`Translation Radar` is an external market-intelligence platform for tech scouts tracking early translation signals across universities, federal labs, patents, publications, and commercialization funding.

The operating principle is simple:

- scheduled adapters ingest public technology and research signals
- normalization and enrichment turn fragmented records into a scoutable graph
- deterministic scoring and retrieval produce ranked opportunities
- human scouts use those outputs for outreach, diligence, and landscape work

The API layer should not run heavy prediction or entity resolution inside the request path.

## Core Domains

### Institution
- source type, source URL, institution class, refresh cadence, parser state

### Technology Listing
- title, description, institution, contact, posted date, category tags, source-specific metadata

### Researcher
- identity resolution across author names, ORCID, internal IDs, and departments

### Publication
- title, abstract, publication date, venue, source IDs, technology tags, commercialization relevance

### Grant
- sponsor, award amount, date, keywords, translational relevance

### Patent or IP Signal
- application number, publication number, assignee, status, dates, linked technology themes

### Translation Event
- SBIR or STTR award, startup formation, licensing event, financing milestone, public filing signal

### Alert
- signal type, score, reasons, recommended action, evidence, review status

## Initial Agent Set

### Scout Agent
Matches a scout thesis to ranked technologies, publications, grants, and translation signals.

### Publication Surveillance Agent
Monitors new papers and attaches them to known researchers, labs, and categories.

### Landscape Agent
Builds a market map for a technical area across institutions, maturity, funding, and patent context.

### Outcome Tracker Agent
Links later commercialization outcomes back to earlier signals for retrospective ranking improvement.

## Production Shape

### Ingestion Jobs
- scheduled adapters for Inteum RSS, priority custom institution sites, federal labs, OpenAlex, Crossref, PubMed, ORCID, PatentsView, and translation-funding sources

### Normalization Layer
- entity resolution
- taxonomy tagging
- evidence extraction
- common schema normalization with source-specific JSON sidecars

### Intelligence Layer
- deterministic scoring
- retrieval over relevant records
- ranking and recommendation generation
- thesis matching and landscape synthesis

### Application Layer
- FastAPI for APIs
- separate UI later for scout search, thesis workflows, ranked opportunity review, and landscape brief generation

### Persistence Layer
- PostgreSQL for workflow and core entities
- optional vector index for retrieval-backed briefing

## Why Start Here

The fastest credible rebuild is not a generic chat app. It is a service that can:

1. ingest heterogeneous public technology and research signals
2. normalize them into a scoutable schema
3. score and rank opportunities deterministically
4. return explainable outputs that can support scout workflows and later agent layers
