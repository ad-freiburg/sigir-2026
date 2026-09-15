# Mails sent by the SIGIR 2026 program chairs

One file per mail campaign, in the input format of `ortler mail`
(https://github.com/ad-freiburg/ortler): a few header lines, a blank line,
then the body in Markdown. The file name starts with the date on which the
mail was sent.

The `# Query:` line points to the SPARQL query that computed the list of
recipients, in `../queries/mails/`. Columns of the query result can be used
as `{{placeholders}}` in the subject and body; `{{name}}`,
`{{firstname_or_fullname}}`, and the like are filled from the profile of
the recipient.

The `To:` lines with the actual recipients have been removed, as well as
all personal names except those of the program chairs.
