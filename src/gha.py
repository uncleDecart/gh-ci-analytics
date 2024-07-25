import requests
import math
from datetime import datetime
from datetime import date
import json
from collections import defaultdict

"""
GitHubActionsAPI is a class which wraps calling to GitHub APIs to get
data about runs
"""
class GitHubActionsAPI:
    def __init__(self, base_url: str, org: str, repo: str, access_token: str):
        self._base_url = base_url
        self._org = org
        self._repo = repo
        self._access_token = access_token

        self._workflow_runs_url = f"{self._base_url}/repos/{self._org}/{self._repo}/actions/runs"
        self._headers = {
            "Authorization": f"token {self._access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def page_count(self, per_page: int = 100) -> int:
        params = {
            "per_page": per_page,
        }

        response = requests.get(self._workflow_runs_url, headers=self._headers, params=params)
        response.raise_for_status()
        workflow_runs = response.json()

        return math.ceil(workflow_runs["total_count"] / per_page)


    def load_workflows(self, page: int = 1, per_page: int = 100):
        params = {
            "per_page" : per_page,
            "page": page,
        }

        response = requests.get(self._workflow_runs_url, headers=self._headers, params=params)
        response.raise_for_status()
        workflow_runs = response.json()

        return workflow_runs["workflow_runs"]

    def get_run_approvals(self, run_id):
        url = f"{self._workflow_runs_url}/{run_id}/approvals"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def get_run(self, run_id):
        url = f"{self._workflow_runs_url}/{run_id}"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()
        return response.json()


"""
GitHubWorkflowStat is a class which wraps calling to GitHub APIs to get
data about runs
"""
class GitHubWorkflowStat:
    def __init__(self, workflows):
        self._workflows = workflows

    def get_field_count(self, field: str):
        count = defaultdict(int)

        for wf in self._workflows:
            count[wf[field]] += 1

        return count

    def groupby(self, field: str):
        groups = defaultdict(list)

        for wf in self._workflows:
            groups[wf[field]].append(wf)

        return groups

    def pick(self, fields):
        data = []

        for wf in self._workflows:
            entry = []

            for field in fields:
                entry.append(wf[field])
            data.append(entry)


        return data

    def save(self, path: str):
        with open(path, 'w') as file:
            json.dump(self._workflows, file)

    def load(self, path: str):
        with open(path, 'r') as file:
            self._workflows = json.load(file)

def duration_time(workflow):
    return datetime.fromisoformat(workflow['updated_at']) - datetime.fromisoformat(workflow['run_started_at'])
