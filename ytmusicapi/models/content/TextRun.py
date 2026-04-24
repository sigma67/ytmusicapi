from typing import TypedDict

type TextRun = HyperLink | PlainText


class HyperLink(TypedDict):
    text: str
    url: str


class PlainText(TypedDict):
    text: str
