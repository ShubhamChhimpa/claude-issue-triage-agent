# claude-issue-triage-agent

A Claude-powered GitHub Action that triages newly opened issues: it classifies
the issue (bug / feature / question / docs), estimates priority, writes a short
summary, and suggests labels — restricted to labels that already exist in the
target repository. It never creates new labels and never closes or modifies
issues beyond commenting and labeling.

## Status

Work in progress. See `triage_agent/` for the core logic and `action.yml` for
the composite GitHub Action definition (added in a later commit).

## Development

```bash
pip install -e ".[dev]"
pytest
```

Full usage instructions (secrets, permissions, example consumer workflow) will
be added once the action is wired up end to end.
