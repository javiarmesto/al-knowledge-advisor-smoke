"""Collect the two Barista pilot events using GitHub REST; never execute event content."""
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen


def require(condition, message):
    if not condition:
        raise ValueError(message)


def collect(event, payload, repository, author, api):
    if event == "issues":
        require(payload["action"] == "opened", "Expected issues.opened")
        hint = payload["issue"]
        number = int(hint["number"])
        issue = api(f"issues/{number}")
        require("pull_request" not in issue and issue["state"] == "open" and issue["user"]["login"] == author,
                "Issue state or author changed")
        require(issue["title"] == "Preparar la autenticación del envío de incidencias de Barista a un servicio externo",
                "Outside the issue pilot")
        require(issue["comments"] <= 10, "Issue discussion too large for pilot")
        comments = api(f"issues/{number}/comments?per_page=11")
        require(len(comments) == issue["comments"], "Issue discussion changed while capturing it")
        return dict(kind="issue", repository=repository, number=number, title=issue["title"], body=issue["body"] or "",
                    updatedAt=issue["updated_at"], comments=[c["body"] for c in comments])
    require(event == "workflow_run", "Unexpected event")
    run = api("actions/runs/" + str(int(payload["workflow_run"]["id"])))
    require(run["event"] == "pull_request" and run["conclusion"] == "success" and run["actor"]["login"] == author
            and run["path"] == ".github/workflows/advisor-pr-intake.yml" and run["head_repository"]["full_name"] == repository
            and len(run["pull_requests"]) == 1, "Untrusted or ambiguous intake")
    number = int(run["pull_requests"][0]["number"])
    pr = api(f"pulls/{number}")
    require(pr["state"] == "open" and not pr["draft"] and pr["user"]["login"] == author and
            pr["head"]["repo"]["full_name"] == pr["base"]["repo"]["full_name"] == repository and
            pr["base"]["ref"] == "main" and pr["head"]["ref"] == "pilot/barista-export-key" and
            pr["head"]["sha"] == run["head_sha"] and pr["changed_files"] == 1, "PR no longer matches pilot intake")
    files = api(f"pulls/{number}/files?per_page=2")
    require(len(files) == 1 and files[0]["filename"] == "App/src/DataModel/BRISalesSetupExt.TableExt.al"
            and files[0]["status"] == "modified", "Unexpected pilot diff")
    file = files[0]
    patch = file.get("patch", "")
    lines = patch.splitlines()
    require(patch and sum(l.startswith("+") for l in lines) == file["additions"] and
            sum(l.startswith("-") for l in lines) == file["deletions"], "Incomplete patch")
    after = api(f"pulls/{number}")
    require(all(after[k]["sha"] == pr[k]["sha"] for k in ("head","base")) and not after["draft"] and after["state"] == "open",
            "PR changed while reading its patch")
    return dict(kind="pull_request", repository=repository, number=number, title=pr["title"], body=pr["body"] or "",
                baseSha=pr["base"]["sha"], headSha=pr["head"]["sha"], baseRef=pr["base"]["ref"],
                files=[dict(path=file["filename"], patch=patch)], intakeRun=run["id"])


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    require(re.fullmatch(r"[\w.-]+/[\w.-]+", repository), "Invalid repository")
    def api(path):
        request = Request(f"https://api.github.com/repos/{repository}/{path}",
                          headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"], "Accept": "application/vnd.github+json"})
        with urlopen(request, timeout=20) as response:
            return json.load(response)
    payload = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    require(payload["repository"]["full_name"] == repository, "Event repository mismatch")
    task = collect(os.environ["GITHUB_EVENT_NAME"], payload, repository, os.environ["PILOT_AUTHOR"], api)
    task["host"] = {key: os.environ[key] for key in ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_WORKFLOW_REF")}
    data = json.dumps(task, ensure_ascii=False, indent=2).encode()
    require(len(data) <= 160000, "Task context too large")
    Path(os.environ["RUNNER_TEMP"], "advisor-context.json").write_bytes(data)


if __name__ == "__main__":
    main()
