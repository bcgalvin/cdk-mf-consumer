from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, WrapValidator, field_validator, model_validator


def validate_timezone(v: datetime | int, handler) -> datetime:
    if isinstance(v, int):
        return datetime.fromtimestamp(v, tz=UTC)
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=UTC)
        return handler(v)
    return handler(v)


TZAwareDatetime = Annotated[datetime, WrapValidator(validate_timezone)]
PositiveInt = Annotated[int, Field(gt=0)]


class HNItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    id: int = Field(..., gt=0, description="Unique identifier for the item")
    type: str = Field(..., description="Type of HN item")
    by: str | None = Field(None, min_length=1, description="Username of the author")
    time: TZAwareDatetime = Field(..., description="Creation timestamp")
    dead: bool = Field(False, description="Whether item is dead")
    deleted: bool = Field(False, description="Whether item is deleted")
    kids: list[int] = Field(default_factory=list, description="Child comment IDs")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = {"story", "comment", "job", "poll", "pollopt"}
        if v not in valid_types:
            raise ValueError(f"Invalid item type: {v}. Must be one of {valid_types}")
        return v


class HNStoryItem(HNItem):
    type: Literal["story"] = "story"
    title: str | None = Field(None, min_length=1, description="Story title. Required unless story is deleted.")
    url: str | None = Field(None, description="Story URL")
    text: str | None = Field(None, description="Story text for Ask HN")
    score: int | None = Field(None, ge=0, description="Story score")
    descendants: int | None = Field(None, ge=0, description="Number of comments")

    @model_validator(mode="after")
    def validate_title_if_not_deleted(self) -> "HNStoryItem":
        if not self.deleted and not self.title:
            raise ValueError("title field is required for non-deleted stories")
        return self


class HNCommentItem(HNItem):

    type: Literal["comment"] = "comment"
    text: str | None = Field(None, min_length=1, description="Comment text. Required unless comment is deleted.")
    parent: int = Field(..., gt=0, description="ID of parent item")

    @model_validator(mode="after")
    def validate_text_if_not_deleted(self) -> "HNCommentItem":
        if not self.deleted and not self.text:
            raise ValueError("text field is required for non-deleted comments")
        return self


class HNJobItem(HNItem):

    type: Literal["job"] = "job"
    title: str | None = Field(None, min_length=1, description="Job title. Required unless job is deleted.")
    text: str | None = Field(None, description="Job description")
    url: str | None = Field(None, description="Job URL")
    score: int | None = Field(None, ge=0, description="Job post score")

    @model_validator(mode="after")
    def validate_title_if_not_deleted(self) -> "HNJobItem":
        if not self.deleted and not self.title:
            raise ValueError("title field is required for non-deleted jobs")
        return self


class HNPollItem(HNItem):

    type: Literal["poll"] = "poll"
    title: str | None = Field(None, min_length=1, description="Poll title. Required unless poll is deleted.")
    text: str | None = Field(None, description="Poll text")
    score: int | None = Field(None, ge=0, description="Poll score")
    parts: list[int] = Field(..., description="List of poll option IDs")
    descendants: int | None = Field(None, ge=0, description="Number of comments")

    @model_validator(mode="after")
    def validate_title_if_not_deleted(self) -> "HNPollItem":
        if not self.deleted and not self.title:
            raise ValueError("title field is required for non-deleted polls")
        return self


class HNPollOptItem(HNItem):

    type: Literal["pollopt"] = "pollopt"
    text: str | None = Field(None, min_length=1, description="Poll option text. Required unless option is deleted.")
    poll: int = Field(..., gt=0, description="ID of parent poll")
    score: int | None = Field(None, ge=0, description="Number of votes")

    @model_validator(mode="after")
    def validate_text_if_not_deleted(self) -> "HNPollOptItem":
        if not self.deleted and not self.text:
            raise ValueError("text field is required for non-deleted poll options")
        return self
