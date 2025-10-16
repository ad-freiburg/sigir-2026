# Code and documentation surrounding the SIGIR 2026 Full Paper Researc Track

## AI Reviews

Generate AI-based reviews for a given list of PDF files. Install as follows and
type `review --help` for more information.

```
git clone git@github.com:ad-freiburg/sigir-2026.git
cd sigir-2026/ai-reviews
pipx install -e .
eval "$(register-python-argcomplete review)"
review <some_folder>/*.pdf
```
