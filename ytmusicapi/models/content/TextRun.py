from typing import TypedDict


class HyperLink(TypedDict):
    text: str
    url: str


class PlainText(TypedDict):
    text: str


TextRun = HyperLink | PlainText
