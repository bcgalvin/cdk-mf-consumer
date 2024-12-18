from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from cdk_mf_consumer.models.base_models import HNItem, TZAwareDatetime
from cdk_mf_consumer.models.user_models import HNUser

PositiveInt = Annotated[int, Field(gt=0)]


class MaxItemResponse(BaseModel):
    
    model_config = ConfigDict(strict=True, frozen=True)
    
    id: PositiveInt = Field(..., description="Maximum item ID from HN API")
    timestamp: TZAwareDatetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timestamp when max ID was retrieved"
    )


class UpdatesResponse(BaseModel):

    model_config = ConfigDict(strict=True, frozen=True)

    items: list[int] = Field(..., description="Updated item IDs")
    profiles: list[str] = Field(..., description="Updated usernames")


class ItemListResponse(BaseModel):
    
    model_config = ConfigDict(strict=True, frozen=True)
    
    items: list[int] = Field(..., description="List of item IDs")


class UpdatesTracker(BaseModel):

    model_config = ConfigDict(strict=True, frozen=True)
    
    since: TZAwareDatetime
    include_profiles: bool = True
    updated_items: list[HNItem] = Field(default_factory=list, description="Updated items since 'since'")
    updated_users: list[HNUser] = Field(default_factory=list, description="Updated user profiles since 'since'")
