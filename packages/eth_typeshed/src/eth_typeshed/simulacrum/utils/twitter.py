from typing import Any

from eth_rpc.types import Bytes32Hex, EIP712Model, primitives
from pydantic import ConfigDict, Field


def get_tweet_timestamp(tid: int) -> int:
    offset = 1288834974657
    tstamp = (tid >> 22) + offset
    return int(tstamp)


class UserMention(EIP712Model):
    id: Bytes32Hex
    screen_name: str = Field(alias="screenName")
    start_index: primitives.uint256 = Field(alias="startIndex")
    end_index: primitives.uint256 = Field(alias="endIndex")

    model_config = ConfigDict(populate_by_name=True)

    @staticmethod
    def from_mention(mention: dict[str, Any]):
        return UserMention(
            id=mention["id_str"],
            screen_name=mention["screen_name"],
            start_index=mention["indices"][0],
            end_index=mention["indices"][1],
        )


class Tweet(EIP712Model):
    id: Bytes32Hex
    user_id: Bytes32Hex = Field(alias="userId")
    created_at: primitives.uint64 = Field(alias="createdAt")
    conversation_id: Bytes32Hex = Field(alias="conversationId")
    full_text: primitives.string = Field(alias="fullText")
    in_reply_to_status_id: Bytes32Hex = Field(
        alias="inReplyToStatusId", default=primitives.bytes32(b"")
    )
    in_reply_to_user_id: Bytes32Hex = Field(
        alias="inReplyToUserId", default=primitives.bytes32(b"")
    )
    is_quote: bool = Field(alias="isQuote")
    mentions: list[UserMention] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @property
    def id_int(self):
        return int(self.id.hex(), 16)
