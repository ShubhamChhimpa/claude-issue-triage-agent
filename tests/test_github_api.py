from unittest.mock import MagicMock, patch

from triage_agent.github_api import add_labels, get_repo_labels, post_comment


def _mock_response(json_data=None, status=200):
    resp = MagicMock()
    resp.json.return_value = json_data or {}
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    return resp


@patch("triage_agent.github_api.requests.get")
def test_get_repo_labels_returns_label_names(mock_get):
    mock_get.return_value = _mock_response(
        [{"name": "bug"}, {"name": "docs"}]
    )

    labels = get_repo_labels("owner", "repo", "tok")

    assert labels == ["bug", "docs"]
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.github.com/repos/owner/repo/labels"
    assert kwargs["headers"]["Authorization"] == "Bearer tok"


@patch("triage_agent.github_api.requests.post")
def test_post_comment_sends_body(mock_post):
    mock_post.return_value = _mock_response()

    post_comment("owner", "repo", 42, "hello", "tok")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.github.com/repos/owner/repo/issues/42/comments"
    assert kwargs["json"] == {"body": "hello"}


@patch("triage_agent.github_api.requests.post")
def test_add_labels_sends_label_list(mock_post):
    mock_post.return_value = _mock_response()

    add_labels("owner", "repo", 42, ["bug", "docs"], "tok")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.github.com/repos/owner/repo/issues/42/labels"
    assert kwargs["json"] == {"labels": ["bug", "docs"]}


@patch("triage_agent.github_api.requests.post")
def test_add_labels_skips_request_when_no_labels(mock_post):
    add_labels("owner", "repo", 42, [], "tok")

    mock_post.assert_not_called()


@patch("triage_agent.github_api.requests.get")
def test_get_repo_labels_raises_on_error_status(mock_get):
    resp = _mock_response(status=404)
    resp.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = resp

    try:
        get_repo_labels("owner", "repo", "tok")
        assert False, "expected an exception"
    except Exception as exc:
        assert "404" in str(exc)
