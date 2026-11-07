# SPARQL queries on the SIGIR 2026 review data

The queries run on the RDF data produced by `ortler dump`
(https://github.com/ad-freiburg/ortler), indexed with QLever. Each
subdirectory has a README listing its queries:

- [`statistics/`](statistics/README.md): the queries behind the charts and statistics in our report;
  a first-line `#defaultView:` directive selects the chart type in the
  query UI.
- [`reviewing-process/`](reviewing-process/README.md): the queries we used during the reviewing process,
  from progress monitoring to identifying problems.
- [`mails/`](mails/README.md): the queries that computed the recipients (and placeholders) of
  the mails in `../mails/`, one query per mail.

Profile IDs of individual persons (other than the program chairs) have
been replaced by `Redacted_NameN`.
