# OpenReview CLI Tool (orsig) for SIGIR 2026

## Project Structure
- CLI tool for OpenReview API with commands: `update`, `dump`, `profile`, `submissions`, `recruitment`, `mail`
- Cache-based workflow: `update` syncs with OpenReview, `dump` outputs cached data as RDF
- Uses singleton client pattern for API authentication (both v1 and v2 APIs)

## Key Files
- `src/orsig/main.py`: CLI entry point with argparse
- `src/orsig/client.py`: Singleton OpenReview client management (v1 and v2 APIs)
- `src/orsig/profile.py`: ProfileWithPapers class with caching and RDF export
- `src/orsig/rdf.py`: Rdf class for triple collection and Turtle serialization
- `src/orsig/qlever.py`: QLever SPARQL query functions
- `src/orsig/commands/`: Individual command implementations
  - `update.py`: Incremental cache sync with OpenReview
  - `dump.py`: Output all cached data as RDF
  - `recruitment.py`: Manage PC/SPC/AC membership
  - `submissions.py`: Show cached submission summary
  - `mail.py`: Send emails via OpenReview API

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
- Person triples: `:id`, `:state`, `:role`, `:status`, `:gender`, `:dblp_id`, `:orcid`, `:email`, `:position`, `:institution`, `:publication`, `:dblp_publication`, `:num_publications`
- Submission triples: `:title`, `:abstract`, `:author`, `:authors`, `:num_authors`, `:has_pdf`, `:created_on`, `:last_modified_on`, AI review fields

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

## Logging
Use `from .log import log` and then `log.info()`, `log.warning()`, `log.error()` for all output messages. Do not use `print()` for logging.

## Cache Structure
The cache directory (set via `CACHE_DIR` or `--cache-dir`) contains:
- `metadata.json`: Last update timestamp
- `profiles/`: Profile JSON files (by canonical ID, e.g., `Hannah_Bast1.json`)
- `profiles/_id_mapping.json`: Email → canonical profile ID mapping
- `submissions/`: Submission JSON files
- `groups/`: Group membership (Reviewers.json, Area_Chairs.json, etc.)
- `recruitment/reduced_loads.json`: Reduced load entries
- `reviews/`: AI review JSON files
- `pdfs/`: Downloaded submission PDFs

**Important:** Groups cache stores members by email address (e.g., `user@example.com`), not profile ID. The `_id_mapping.json` file maps emails to canonical profile IDs (e.g., `~User_Name1`).

## Profile State
Profiles have a `state` field (not included in OpenReview's `to_json()`) that indicates their status:
- `Active Institutional` - Verified institutional email
- `Active` - Manually activated
- `Active Automatic` - Auto-activated
- `Needs Moderation` - Awaiting review
- `Inactive` - Deactivated
- `Rejected` - Profile rejected
- `Blocked` - Account blocked

The `state` field is saved to cache and output as `:state` triple in RDF.

## Update Command and --recache Options
The `update` command syncs the cache with OpenReview:
- `orsig update` - Incremental update (only changed data since last update)
- `orsig update --recache submissions` - Re-fetch all submissions
- `orsig update --recache profiles` - Re-fetch profile metadata only (1 API call per profile)
- `orsig update --recache profiles-with-publications` - Re-fetch profiles + publications (3 API calls per profile)
- `orsig update --recache all` - Re-fetch submissions + profiles-with-publications

The options are NOT hierarchical (except `profiles` < `profiles-with-publications`). DBLP publication scanning only runs during incremental updates.

## Common Workflow
1. `orsig update` - Sync cache with OpenReview (incremental)
2. `orsig update --recache all` - Force full cache refresh
3. `orsig dump --output data.rdf` - Output all cached data as RDF
4. `orsig submissions` - Show summary of cached submissions
5. `orsig recruitment --role pc --add invited user@example.com` - Add to PC

## Other Commands
- `orsig profile ~Hannah_Bast1 --as-rdf`: Get single profile with RDF output
- `orsig mail message.txt --dry-run`: Preview email without sending
- `orsig mail message.txt --recipients-from-sparql-query HASH`: Send to SPARQL results

## Rate Limiting
OpenReview API has rate limits (3 requests per time window). Use cache-based workflow to minimize API calls. If rate limited, wait ~30 seconds.
