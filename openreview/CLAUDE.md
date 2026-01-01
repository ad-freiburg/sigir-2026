# OpenReview CLI Tool (orsig) for SIGIR 2026

## Project Structure
- CLI tool for OpenReview API with commands: `profile`, `submissions`, `pcmembers`, `invitations`
- Supports JSON and RDF output formats via `--as-rdf` option
- Uses singleton client pattern for API authentication
- Profile caching system for performance

## Key Files
- `src/orsig/main.py`: CLI entry point with argparse
- `src/orsig/client.py`: Singleton OpenReview client management
- `src/orsig/profile.py`: ProfileWithPapers class with caching and RDF export
- `src/orsig/rdf.py`: Rdf class for triple collection and Turtle serialization
- `src/orsig/commands/`: Individual command implementations

## Authentication & Environment
Set in `.env` file:
```
OPENREVIEW_API_URL=https://api2.openreview.net
OPENREVIEW_USERNAME=your_email
OPENREVIEW_PASSWORD=your_password
OPENREVIEW_VENUE_ID=SIGIR.org/2026/Conference
OPENREVIEW_IMPERSONATE_GROUP=venue_organizer_group
RDF_DEFAULT_PREFIX=http://openreview.net/
```

## RDF System
- `Rdf` class collects triples via `add_triple(subject, predicate, object)`
- `as_turtle()` outputs proper Turtle format with semicolons/commas
- Used by profile, submissions, and pcmembers commands

## Code Style
Each .py file should be formatted according to `ruff format % && ruff check --fix %`

## Common Tasks
- `./venv/bin/orsig profile ~Hannah_Bast1 --as-rdf`: Get profile with RDF output
- `./venv/bin/orsig pcmembers reviewers --with-profiles`: Get reviewers with profile data
- Profile data cached in `./profiles/` directory for performance