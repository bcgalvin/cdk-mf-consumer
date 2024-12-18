from typing import Any, Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from cdk_mf_consumer.models.base_models import (
    HNCommentItem,
    HNItem,
    HNJobItem,
    HNPollItem,
    HNPollOptItem,
    HNStoryItem,
)
from cdk_mf_consumer.models.response_models import MaxItemResponse, UpdatesResponse
from cdk_mf_consumer.models.user_models import HNUser


class HNClient:

    _instance: Optional["HNClient"] = None
    base_url: str = "https://hacker-news.firebaseio.com/v0"
    client: httpx.Client

    def __init__(self):
        if not hasattr(self, "client"):
            self.client = httpx.Client(
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=60.0,
                    write=5.0,
                    pool=10.0,
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=10,
                    max_connections=20,
                ),
            )

    def __new__(cls) -> "HNClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __del__(self) -> None:
        if hasattr(self, "client"):
            self.client.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def _get(self, endpoint: str) -> Any:
        try:
            response = self.client.get(f"{self.base_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout accessing {endpoint}: {e!s}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error accessing {endpoint}: {e!s}")
            raise

    def get_item(self, item_id: int) -> HNItem | None:
        try:
            data = self._get(f"item/{item_id}.json")
            if not data:
                return None

            item_type = data.get("type")
            if item_type == "story":
                return HNStoryItem(**data)
            elif item_type == "comment":
                return HNCommentItem(**data)
            elif item_type == "job":
                return HNJobItem(**data)
            elif item_type == "poll":
                return HNPollItem(**data)
            elif item_type == "pollopt":
                return HNPollOptItem(**data)
            else:
                logger.warning(f"Unknown item type: {item_type}")
                return None
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {e!s}")
            return None

    def get_user(self, username: str) -> HNUser | None:
        try:
            data = self._get(f"user/{username}.json")
            if not data:
                return None
            return HNUser(**data)
        except Exception as e:
            logger.error(f"Error getting user {username}: {e!s}")
            return None

    def get_max_item_id(self) -> MaxItemResponse | None:
        try:
            max_id = self._get("maxitem.json")
            return MaxItemResponse(id=max_id)
        except Exception as e:
            logger.error(f"Error getting max item ID: {e!s}")
            return None

    def get_updates(self) -> UpdatesResponse | None:
        try:
            data = self._get("updates.json")
            if not data:
                return None
            return UpdatesResponse(**data)
        except Exception as e:
            logger.error(f"Error getting updates: {e!s}")
            return None

