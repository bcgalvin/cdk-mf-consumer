from pydantic import BaseModel, ConfigDict, Field

from cdk_mf_consumer.models.base_models import TZAwareDatetime


class HNUser(BaseModel):

    model_config = ConfigDict(strict=True, frozen=True)

    id: str = Field(..., min_length=1, description="Username")
    created: TZAwareDatetime = Field(..., description="Account creation timestamp")
    karma: int = Field(..., ge=0, description="User's karma points")
    about: str | None = Field(None, min_length=1, description="User's profile text")
    submitted: list[int] = Field(default_factory=list, description="Submitted item IDs")
