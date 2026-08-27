# slim-lite

A small people-search CRM. Natural-language searches are parsed into filter
JSON by Gemini Flash Lite, executed against a SQLite database, and rendered on
a single static page.

First time here? Read [CANDIDATE-BRIEF.md](CANDIDATE-BRIEF.md), then
[TASK.md](TASK.md).

## Setup

```
make setup   # install dependencies
make seed    # create and populate data/app.db (deterministic)
make test    # run the test suite
make run     # serve the app on http://localhost:8000
```

`reset.sh` restores the repo to its starting state (discards changes, reseeds).

## Architecture

- `app/seed.py` builds a SQLite database of orgs, people, and tags. All data is
  synthetic and identical on every reseed.
- `app/llm.py` calls Gemini Flash Lite: `parse_query(text)` turns any search
  phrase into filter JSON. It reads `GOOGLE_API_KEY` from the environment
  (already set for you in the interview environment).
- `POST /query` calls `parse_query`, hands the result to
  `app/filters.py::execute_filter(filter_json, org_id)`, and returns the
  matching people plus the filter that produced them.
- The LLM always returns valid, well-formed filter JSON, so `execute_filter`
  can assume its input is clean.
- `static/index.html` is the whole frontend: a search box, example phrases in
  a dropdown (any phrase works), and a results table with a count.

Filter JSON shape:

```json
{"op": "and", "clauses": [{"field": "city", "cmp": "eq", "value": "Houston"}]}
```

Fields: `city`, `state`, `tag`, `email`. Comparators: `eq`, `contains`.
Clauses are combined with a single flat `and`.

## Endpoints

- `GET /people?org_id=N` — all people in an org
- `GET /tags?org_id=N` — an org's tags
- `POST /query` — body `{"text": "...", "org_id": N}`
