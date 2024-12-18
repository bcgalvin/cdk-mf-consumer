from cdk_mf_consumer.client import HNClient
from cdk_mf_consumer.models.base_models import HNItem
from cdk_mf_consumer.models.response_models import MaxItemResponse, UpdatesResponse
from cdk_mf_consumer.models.user_models import HNUser

client = HNClient()

def get_item(item_id: int) -> HNItem | None:
    return client.get_item(item_id)

def get_user(username: str) -> HNUser | None:
    return client.get_user(username)

def get_max_item_id() -> MaxItemResponse | None:
    return client.get_max_item_id()

def get_updates() -> UpdatesResponse | None:
    return client.get_updates()
