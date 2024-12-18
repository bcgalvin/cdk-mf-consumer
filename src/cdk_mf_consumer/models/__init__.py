from cdk_mf_consumer.models.base_models import HNCommentItem, HNJobItem, HNPollItem, HNPollOptItem, HNStoryItem

HNAnyItem = HNStoryItem | HNCommentItem | HNJobItem | HNPollItem | HNPollOptItem
