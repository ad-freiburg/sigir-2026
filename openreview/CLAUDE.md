# OpenReview CLI Tool (orsig) for SIGIR 2026

## Project Structure
- CLI tool for OpenReview API with commands: `profile`, `submissions`, `pcmembers`, `invitations`, `mail`
- Supports JSON and RDF output formats via `--as-rdf` option
- Uses singleton client pattern for API authentication (both v1 and v2 APIs)
- Profile caching system for performance

## Key Files
- `src/orsig/main.py`: CLI entry point with argparse
- `src/orsig/client.py`: Singleton OpenReview client management (v1 and v2 APIs)
- `src/orsig/profile.py`: ProfileWithPapers class with caching and RDF export
- `src/orsig/rdf.py`: Rdf class for triple collection and Turtle serialization
- `src/orsig/qlever.py`: QLever SPARQL query functions
- `src/orsig/commands/`: Individual command implementations

## OpenReview APIs
OpenReview has TWO APIs that must both be queried to get complete data:
- **API v2** (`api2.openreview.net`): Current API, newer submissions
- **API v1** (`api.openreview.net`): Legacy API, contains most DBLP/ORCID imports

The `get_client()` and `get_client_v1()` functions in `client.py` provide singleton access to both.

## Authentication & Environment
Set in `.env` file:
```
OPENREVIEW_API_URL=https://api2.openreview.net
OPENREVIEW_USERNAME=your_email
OPENREVIEW_PASSWORD=your_password
OPENREVIEW_VENUE_ID=ACM.org/SIGIR/2026/Conference
OPENREVIEW_IMPERSONATE_GROUP=venue_organizer_group
RDF_DEFAULT_PREFIX=http://openreview.net/
CACHE_DIR=orsig-cache
MAIL_FROM=Name <sender@openreview.net>
MAIL_FROM_DIRECT=Name <your_email>
QLEVER_LINK_API=https://qlever.dev/api/link/
QLEVER_QUERY_API=https://qlever.dev/api/sigir-2026
QLEVER_QUERY_API_USERNAME=username
QLEVER_QUERY_API_PASSWORD=password
```

## RDF System
- `Rdf` class collects triples via `add_triple(subject, predicate, object)`
- `as_turtle()` outputs proper Turtle format with semicolons/commas
- Prefixes: `paper:` for papers/submissions, `person:` for profiles
- `paperIri()` handles IDs starting with `-` by using full IRI form
- Used by profile, submissions, and pcmembers commands

## Mail Command
- Sends emails via OpenReview API from a file with headers and body
- Supports `{{name}}` placeholder for personalized emails
- `--recipients-from-sparql-query HASH_OR_URL`: Replace To: field with SPARQL query results
- Converts email-as-profile IDs (like `~user_at_domain_com`) to actual emails
- Continues on failure and reports success/failure counts

## QLever Integration
- `get_sparql_query(short_hash)`: Fetch query from QLever link API
- `issue_sparql_query(query)`: Execute SPARQL query
- `recipients_from_query(hash_or_url)`: Get profile IDs from query results

## Code Style
Each .py file should be formatted according to `/home/bast/.local/bin/ruff format FILE && /home/bast/.local/bin/ruff check --fix FILE`

## Common Tasks
- `orsig profile ~Hannah_Bast1 --as-rdf`: Get profile with RDF output
- `orsig pcmembers reviewers --with-profiles`: Get reviewers with profile data
- `orsig mail message.txt --dry-run`: Preview email without sending
- `orsig mail message.txt --recipients-from-sparql-query https://qlever.dev/sigir-2026/HASH`: Send to SPARQL query results
- Profile data cached in `orsig-cache/profiles/` directory

## Rate Limiting
OpenReview API has rate limits (3 requests per time window). The singleton client pattern minimizes logins. If rate limited, wait ~30 seconds.
