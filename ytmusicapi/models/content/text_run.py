from ..base import YTMusicModel


class HyperLink(YTMusicModel):
    text: str
    url: str


class PlainText(YTMusicModel):
    text: str


TextRun = HyperLink | PlainText
