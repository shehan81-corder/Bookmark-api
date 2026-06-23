from pydantic import BaseModel, AnyHttpUrl, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class TagResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    url: AnyHttpUrl
    title: str
    description: Optional[str] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def title_max_length(cls, v):
        if len(v) > 200:
            raise ValueError("Title must be under 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v):
        if v and len(v) > 500:
            raise ValueError("Description must be under 500 characters")
        return v

    @field_validator("tags")
    @classmethod
    def lowercase_tags(cls, v):
        return [tag.lower().strip() for tag in v]


class BookmarkUpdate(BaseModel):
    url: Optional[AnyHttpUrl] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def title_max_length(cls, v):
        if v and len(v) > 200:
            raise ValueError("Title must be under 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v):
        if v and len(v) > 500:
            raise ValueError("Description must be under 500 characters")
        return v

    @field_validator("tags")
    @classmethod
    def lowercase_tags(cls, v):
        if v:
            return [tag.lower().strip() for tag in v]
        return v


class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str
    description: Optional[str] = None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime
