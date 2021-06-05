from dataclasses import dataclass
from typing import Optional
from typing import Sequence

from radegast import get
from radegast import Radegast


@dataclass
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


@dataclass
class Ad:
    company: str
    url: str
    text: str


@dataclass
class UserDetail:
    data: User
    ad: Ad


@dataclass
class Users:
    page: int
    per_page: int
    total: int
    total_pages: int
    data: Sequence[User]


@dataclass
class UsersParams:
    page: Optional[int] = None
    per_page: Optional[int] = None


class ReqRes(Radegast, base_url="https://reqres.in/api/"):
    users: get(Users, UsersParams)
    user: get(UserDetail).for_path("/users/{id}/")
