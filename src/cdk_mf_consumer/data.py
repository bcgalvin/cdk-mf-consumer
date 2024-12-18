from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import polars as pl

from cdk_mf_consumer.client import HNClient
from cdk_mf_consumer.models.base_models import (
    HNCommentItem,
    HNItem,
    HNJobItem,
    HNPollItem,
    HNPollOptItem,
    HNStoryItem,
)
from cdk_mf_consumer.models.response_models import UpdatesResponse
from cdk_mf_consumer.models.user_models import HNUser


class HNData:

    # Mapping of item types to their plural forms
    PLURAL_FORMS = {
        "story": "stories",
        "comment": "comments",
        "job": "jobs",
        "poll": "polls",
        "pollopt": "pollopts",
        "user": "users",
    }

    def __init__(self):
        # Base schema shared by all item types
        self.base_schema = {
            "id": pl.Int64,
            "type": pl.Utf8,
            "by": pl.Utf8,
            "time": pl.Datetime,
            "dead": pl.Boolean,
            "deleted": pl.Boolean,
            "kids": pl.List(pl.Int64),
        }

        # Type-specific schemas
        self.story_schema = {
            **self.base_schema,
            "title": pl.Utf8,
            "url": pl.Utf8,
            "text": pl.Utf8,
            "score": pl.Int32,
            "descendants": pl.Int32,
        }

        self.comment_schema = {
            **self.base_schema,
            "text": pl.Utf8,
            "parent": pl.Int64,
        }

        self.job_schema = {
            **self.base_schema,
            "title": pl.Utf8,
            "text": pl.Utf8,
            "url": pl.Utf8,
            "score": pl.Int32,
        }

        self.poll_schema = {
            **self.base_schema,
            "title": pl.Utf8,
            "text": pl.Utf8,
            "score": pl.Int32,
            "parts": pl.List(pl.Int64),
            "descendants": pl.Int32,
        }

        self.pollopt_schema = {
            **self.base_schema,
            "text": pl.Utf8,
            "poll": pl.Int64,
            "score": pl.Int32,
        }

        self.user_schema = {
            "id": pl.Utf8,
            "created": pl.Datetime,
            "karma": pl.Int32,
            "about": pl.Utf8,
            "submitted": pl.List(pl.Int64),
            "timestamp": pl.Datetime,  # When the user data was fetched
        }

    @classmethod
    def get_plural_form(cls, item_type: str) -> str:
        return cls.PLURAL_FORMS.get(item_type, f"{item_type}s")

    def group_items_by_type(self, items: Sequence[HNItem]) -> dict[str, list[HNItem]]:
        grouped: dict[str, list[HNItem]] = {
            "story": [],
            "comment": [],
            "job": [],
            "poll": [],
            "pollopt": [],
        }
        
        for item in items:
            if isinstance(item, HNStoryItem):
                grouped["story"].append(item)
            elif isinstance(item, HNCommentItem):
                grouped["comment"].append(item)
            elif isinstance(item, HNJobItem):
                grouped["job"].append(item)
            elif isinstance(item, HNPollItem):
                grouped["poll"].append(item)
            elif isinstance(item, HNPollOptItem):
                grouped["pollopt"].append(item)
        
        return grouped

    def items_to_frames(
        self, items: Sequence[HNItem]
    ) -> dict[str, pl.DataFrame | None]:
        grouped = self.group_items_by_type(items)
        frames = {}
        
        # Convert each group to its specific DataFrame
        if grouped["story"]:
            frames["story"] = pl.DataFrame(
                [item.model_dump() for item in grouped["story"]],
                schema=self.story_schema
            )
        
        if grouped["comment"]:
            frames["comment"] = pl.DataFrame(
                [item.model_dump() for item in grouped["comment"]],
                schema=self.comment_schema
            )
        
        if grouped["job"]:
            frames["job"] = pl.DataFrame(
                [item.model_dump() for item in grouped["job"]],
                schema=self.job_schema
            )
        
        if grouped["poll"]:
            frames["poll"] = pl.DataFrame(
                [item.model_dump() for item in grouped["poll"]],
                schema=self.poll_schema
            )
        
        if grouped["pollopt"]:
            frames["pollopt"] = pl.DataFrame(
                [item.model_dump() for item in grouped["pollopt"]],
                schema=self.pollopt_schema
            )
        
        return frames

    def users_to_frame(self, users: Sequence[HNUser], timestamp: datetime | None = None) -> pl.DataFrame:
        data = []
        fetch_time = timestamp or datetime.now()
        for user in users:
            user_data = user.model_dump()
            user_data["timestamp"] = fetch_time
            data.append(user_data)
        return pl.DataFrame(data, schema=self.user_schema)

    def updates_to_frame(self, updates: UpdatesResponse) -> pl.DataFrame:
        schema = {
            "items": pl.List(pl.Int64),
            "profiles": pl.List(pl.Utf8),
            "timestamp": pl.Datetime,
        }
        data = updates.model_dump()
        data["timestamp"] = datetime.now()  # Add timestamp when data was collected
        return pl.DataFrame([data], schema=schema)

    def write_parquet(
        self,
        df: pl.DataFrame,
        path: str | Path,
        *,
        compression: str = "snappy",
        overwrite: bool = False,
    ) -> None:
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f"File {path} already exists and overwrite=False")
            
        path.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(path, compression=compression)


def process_batch(client: HNClient, item_ids: list[int], stats: dict) -> list[HNItem]:
    items = []
    for item_id in item_ids:
        try:
            if item := client.get_item(item_id):
                items.append(item)
                stats["success"] += 1
                # Track type-specific success
                stats[f"success_{item.type}"] = stats.get(f"success_{item.type}", 0) + 1
            else:
                stats["not_found"] += 1
        except Exception:
            stats["failed"] += 1
    return items


def process_user_batch(client: HNClient, usernames: list[str], stats: dict) -> list[HNUser]:
    users = []
    for username in usernames:
        try:
            if user := client.get_user(username):
                users.append(user)
                stats["success"] += 1
            else:
                stats["not_found"] += 1
        except Exception:
            stats["failed"] += 1
    return users
