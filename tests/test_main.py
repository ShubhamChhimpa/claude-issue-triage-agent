from unittest.mock import ANY, patch

from triage_agent.classifier import TriageResult
from triage_agent.main import _build_comment, run


def _issue_event(action="opened", number=7, title="Bug title", body="Bug body"):
    return {
        "action": action,
        "issue": {"number": number, "title": title, "body": body},
    }


def _pr_event(action="opened", number=9, title="PR title", body="PR body"):
    return {
        "action": action,
        "pull_request": {"number": number, "title": title, "body": body},
    }


def test_run_skips_non_opened_actions():
    event = _issue_event(action="closed")

    result = run(event, "owner/repo", "tok")

    assert result is None


def test_run_skips_events_without_issue_or_pull_request_key():
    event = {"action": "opened"}

    result = run(event, "owner/repo", "tok")

    assert result is None


@patch("triage_agent.main.add_labels")
@patch("triage_agent.main.post_comment")
@patch("triage_agent.main.classify_issue")
@patch("triage_agent.main.get_repo_labels")
def test_run_triages_opened_issue_end_to_end(
    mock_get_labels, mock_classify, mock_post_comment, mock_add_labels
):
    mock_get_labels.return_value = ["bug", "docs"]
    mock_classify.return_value = TriageResult(
        summary="Something broke.", type="bug", priority="high", labels=["bug"]
    )

    event = _issue_event()
    status = run(event, "owner/repo", "tok")

    mock_get_labels.assert_called_once_with("owner", "repo", "tok")
    mock_classify.assert_called_once_with(
        "Bug title", "Bug body", ["bug", "docs"], kind="issue"
    )
    mock_post_comment.assert_called_once()
    mock_add_labels.assert_called_once_with("owner", "repo", 7, ["bug"], "tok")
    assert "Triaged issue #7" in status
    assert "type=bug" in status


@patch("triage_agent.main.add_labels")
@patch("triage_agent.main.post_comment")
@patch("triage_agent.main.classify_issue")
@patch("triage_agent.main.get_repo_labels")
def test_run_triages_opened_pull_request_end_to_end(
    mock_get_labels, mock_classify, mock_post_comment, mock_add_labels
):
    mock_get_labels.return_value = ["bug", "docs"]
    mock_classify.return_value = TriageResult(
        summary="Fixes the bug.", type="bug", priority="medium", labels=["bug"]
    )

    event = _pr_event()
    status = run(event, "owner/repo", "tok")

    mock_get_labels.assert_called_once_with("owner", "repo", "tok")
    mock_classify.assert_called_once_with(
        "PR title", "PR body", ["bug", "docs"], kind="pull_request"
    )
    mock_post_comment.assert_called_once_with("owner", "repo", 9, ANY, "tok")
    mock_add_labels.assert_called_once_with("owner", "repo", 9, ["bug"], "tok")
    assert "Triaged PR #9" in status
    assert "type=bug" in status


def test_build_comment_shows_no_labels_message_when_empty():
    result = TriageResult(summary="s", type="question", priority="low", labels=[])

    comment = _build_comment(result)

    assert "none suggested" in comment
    assert "s" in comment
