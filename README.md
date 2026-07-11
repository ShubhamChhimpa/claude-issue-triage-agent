# claude-issue-triage-agent

A Claude-powered GitHub Action that triages newly opened issues: it classifies
the issue (bug / feature / question / docs), estimates priority, writes a short
summary, and suggests labels — restricted to labels that already exist in the
target repository. It never creates new labels and never closes or modifies
issues beyond commenting and labeling.

## Usage

In the repo you want triaged, create `.github/workflows/triage.yml` (see
[`examples/consumer-workflow.yml`](examples/consumer-workflow.yml)):

```yaml
name: Triage new issues

on:
  issues:
    types: [opened]

permissions:
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: ShubhamChhimpa/claude-issue-triage-agent@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Requirements

- Add an `ANTHROPIC_API_KEY` secret to the consuming repo (Settings → Secrets
  and variables → Actions).
- `secrets.GITHUB_TOKEN` is provided automatically by GitHub Actions — just
  make sure the workflow (or job) grants it `issues: write`, as shown above.

### What it does on each new issue

1. Reads the issue title/body from the `issues` webhook event payload.
2. Fetches the repo's existing labels via the GitHub API.
3. Sends the issue to Claude, asking for a type (`bug`/`feature`/`question`/`docs`),
   a priority (`low`/`medium`/`high`), a short summary, and suggested labels
   drawn *only* from the repo's existing labels.
4. Posts a comment with that classification and applies the suggested labels.

It never invents new labels, never closes or edits the issue body, and falls
back to safe defaults (`question` / `medium` / no labels) if Claude's response
can't be parsed.

### Configuration

- `TRIAGE_MODEL` (optional env var, set at the job/step level) overrides the
  default Claude model used for classification.

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

- `triage_agent/prompts.py` — system prompt and allowed type/priority/label logic.
- `triage_agent/classifier.py` — Anthropic Messages API wrapper + response parsing.
- `triage_agent/github_api.py` — GitHub REST API helper (labels, comments).
- `triage_agent/main.py` — entrypoint that ties the above together.
- `action.yml` — composite GitHub Action definition.
