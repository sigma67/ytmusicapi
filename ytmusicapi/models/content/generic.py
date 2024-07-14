from pydantic import BaseModel


class User(BaseModel):
    name: str
    id: str | None


class Album(BaseModel):
    name: str
    id: str


class FeedbackTokens(BaseModel):
    add: str
    remove: str
