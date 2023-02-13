from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    login: str
    id: int


class Comments(BaseModel):
    id: int
    commit_id: str
    user: User
    body: str
    created_at: datetime


class Commits(BaseModel):
    sha: str
    author: User
    committer: User
    message: str | None = None


class PullRequest(BaseModel):
    id: int
    title: str
    number: int
    created_at: datetime
    requested_reviewers: list[User] = []
    commits: list[Commits] = []
    comments: list[Comments] = []
