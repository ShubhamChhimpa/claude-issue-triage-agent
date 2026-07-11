import requests

API_BASE = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_repo_labels(owner: str, repo: str, token: str) -> list[str]:
    response = requests.get(
        f"{API_BASE}/repos/{owner}/{repo}/labels",
        headers=_headers(token),
        params={"per_page": 100},
        timeout=30,
    )
    response.raise_for_status()
    return [label["name"] for label in response.json()]


def post_comment(owner: str, repo: str, issue_number: int, body: str, token: str) -> None:
    response = requests.post(
        f"{API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments",
        headers=_headers(token),
        json={"body": body},
        timeout=30,
    )
    response.raise_for_status()


def add_labels(owner: str, repo: str, issue_number: int, labels: list[str], token: str) -> None:
    if not labels:
        return
    response = requests.post(
        f"{API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/labels",
        headers=_headers(token),
        json={"labels": labels},
        timeout=30,
    )
    response.raise_for_status()
