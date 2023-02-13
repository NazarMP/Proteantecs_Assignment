import json
import os


import argparse
import requests
from prettytable import PrettyTable

from schemas import PullRequest


class RESTClient:
    BASE_URL = None

    def __init__(self, api_token):
        self.api_token = api_token

    def _make_request(self, http_method, url):
        response = requests.request(
            http_method,
            url,
            headers={'Authorization': f'Bearer {self.api_token}',
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        )
        processed_response = self.process_response(response)
        if processed_response is NotImplemented:
            processed_response = response
        return processed_response

    def make_request(self, http_method, url):
        return self._make_request(http_method, url)

    def process_response(self, response):
        return NotImplemented

    def get(self, url_parts):
        url = self.join_url(url_parts)
        return self.make_request("GET", url)

    def join_url(self, parts):
        url = "/".join(parts)
        if self.BASE_URL:
            url = "/".join([self.BASE_URL, url])
        return url


class GithubRESTClient(RESTClient):
    BASE_URL = "https://api.github.com"

    def process_response(self, response):
        return response.json()

    def get_repository_pulls(self, username, repo, *extra):
        return self.get(("repos", username, repo, "pulls") + tuple(extra))


class BaseVCSFecther:
    def __init__(self, api_client):
        self.api_client = api_client

    def fetch_repository_pulls(self, username, repo):
        raise NotImplementedError

    def fetch_commits(self, username, repo, pull_id):
        raise NotImplementedError

    def fetch_comments(self, username, repo, pull_id):
        raise NotImplementedError


class GithubFetcher(BaseVCSFecther):
    def fetch_repository_pulls(self, username, repo):
        return self.api_client.get_repository_pulls(username, repo)

    def fetch_commits(self, username, repo, pull_id):
        return self.api_client.get_repository_pulls(username, repo, pull_id, 'commits')

    def fetch_comments(self, username, repo, pull_id):
        return self.api_client.get_repository_pulls(username, repo, pull_id, 'comments')


class BaseFormat:
    NAME = None

    def __init__(self, data):
        self.data = data

    def represent(self):
        pass


class TableFormat(BaseFormat):
    NAME = "table"

    def represent(self):
        table = PrettyTable(['id', 'title', 'number', 'created_at',
                                  'requested_reviewers', 'commits', 'comments'])
        table.title = "Pull Requests"
        for pull in self.data:
            table.add_row(pull.dict().values())
        return table


class JSONFormat(BaseFormat):
    NAME = "json"

    def represent(self):
        return json.dumps([i.json() for i in self.data], indent=4)


class BaseVCSObject:
    FORMATS = []

    def format_as(self, format_):
        for formatter in self.FORMATS:
            if formatter.NAME == format_:
                return formatter(self.get_data()).represent()
        raise LookupError(format_)


class GithubRepository(BaseVCSObject):
    FORMATS = [TableFormat, JSONFormat]

    def __init__(self, repo_url, fetcher):
        self.repo_url = repo_url
        self.fetcher = fetcher

    def get_data(self):
        repo_cred = self.repo_url.split('/')[-2:]
        pulls = self.fetcher.fetch_repository_pulls(*repo_cred)
        for pull in pulls:
            yield PullRequest(
                id=pull['id'],
                title=pull['title'],
                number=pull['number'],
                created_at=pull['created_at'],
                requested_reviewers=pull['requested_reviewers'],
                commits=self.fetcher.fetch_commits(*repo_cred, str(pull['number'])),
                comments=self.fetcher.fetch_comments(*repo_cred, str(pull['number'])),
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo", help="Specify repository url")
    parser.add_argument("-t", "--token", help="Specify GitHub Token")
    parser.add_argument("-f", "--format", help="Specify format")
    args = parser.parse_args()

    res = GithubRepository(
        args.repo,
        fetcher=GithubFetcher(
            api_client=GithubRESTClient(
                api_token=args.token
            )
        )
    ).format_as(args.format)

    print(res)
