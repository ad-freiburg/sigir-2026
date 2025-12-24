# Tools surrounding the SIGIR 2026 Full Paper Research Track (and maybe also other tracks)

NOTE: The installation commands in the instructions below use `pipx`. You can also use `pip` in a virtual environment of your choice, or `uv`.

## OpenReview tool

A general-purpose tool for queries and actions for an OpenReview conference using the API.

```
git clone git@github.com:ad-freiburg/sigir-2026.git
cd sigir-2026/openreview
pipx install -e .
eval "$(register-python-argcomplete review)"
orsig --help
```

You can set the API URL, username, password, and conference via command-line options, or, more conveniently, via a `.env` file like the following (adapt as needed):

```
OPENREVIEW_API_URL=https://dev-api2.openreview.net
OPENREVIEW_USERNAME=...
OPENREVIEW_PASSWORD=...
OPENREVIEW_VENUE_ID=ACM.org/SIGIR/2026/Conference
```

## AI Reviews

Generate AI-based reviews for a given list of PDF files. Install as follows and type `review --help` for more information. You must set a valid OpenAI API key using `export OPENAI_API_KEY=...`

```
git clone git@github.com:ad-freiburg/sigir-2026.git
cd sigir-2026/ai-reviews
pipx install -e .
eval "$(register-python-argcomplete review)"
review <some_folder>/*.pdf
```
