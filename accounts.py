from typing import NamedTuple


class LoginInfo(NamedTuple):
    LOGIN:         int
    PASSWORD:      str
    SERVER:        str
    TERMINAL_PATH: str


class Accounts:
    exness: LoginInfo = LoginInfo(
        LOGIN=...,
        PASSWORD="...",
        SERVER="...",
        TERMINAL_PATH="..."
    )


