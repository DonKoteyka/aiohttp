from abc import ABC
from typing import Optional

import pydantic


class CreateArticle(pydantic.BaseModel):
    article: str
    description: str
    owner: str


class UpdateArticle(pydantic.BaseModel):
    article: Optional[str]
    description: Optional[str]
    owner: Optional[str]
