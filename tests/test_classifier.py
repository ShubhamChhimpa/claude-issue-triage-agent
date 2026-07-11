import json
from unittest.mock import MagicMock

from triage_agent.classifier import TriageResult, classify_issue
from triage_agent.prompts import build_user_message


def _make_client(response_text: str) -> MagicMock:
    client = MagicMock()
    content_block = MagicMock()
    content_block.text = response_text
    client.messages.create.return_value = MagicMock(content=[content_block])
    return client


def test_classify_issue_happy_path():
    payload = {
        "summary": "Login button does nothing on Safari.",
        "type": "bug",
        "priority": "high",
        "labels": ["bug", "safari"],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(
        title="Login broken on Safari",
        body="Clicking login does nothing.",
        allowed_labels=["bug", "safari", "docs"],
        client=client,
    )

    assert result == TriageResult(
        summary=payload["summary"],
        type="bug",
        priority="high",
        labels=["bug", "safari"],
    )
    client.messages.create.assert_called_once()


def test_classify_issue_filters_labels_not_in_allowed_list():
    payload = {
        "summary": "Some issue.",
        "type": "feature",
        "priority": "low",
        "labels": ["bug", "made-up-label"],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(
        title="t", body="b", allowed_labels=["bug"], client=client
    )

    assert result.labels == ["bug"]


def test_classify_issue_rejects_invalid_type_and_priority():
    payload = {
        "summary": "Some issue.",
        "type": "not-a-real-type",
        "priority": "urgent!!",
        "labels": [],
    }
    client = _make_client(json.dumps(payload))

    result = classify_issue(title="t", body="b", allowed_labels=[], client=client)

    assert result.type == "question"
    assert result.priority == "medium"


def test_classify_issue_falls_back_on_malformed_json():
    client = _make_client("not valid json at all")

    result = classify_issue(title="t", body="b", allowed_labels=["bug"], client=client)

    assert result.type == "question"
    assert result.priority == "medium"
    assert result.labels == []


def test_build_user_message_includes_title_body_and_labels():
    message = build_user_message("Title here", "Body here", ["bug", "docs"])

    assert "Title here" in message
    assert "Body here" in message
    assert "bug, docs" in message


def test_build_user_message_handles_empty_body():
    message = build_user_message("Title here", "", [])

    assert "(no description provided)" in message
    assert "(none available)" in message
