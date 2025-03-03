from typing import Optional, Literal, Self

from pydantic import BaseModel, model_validator, Field

from app.models import ChatTypeEnum


class CreateChatRequest(BaseModel):
    name: Optional[str] = Field(None, alias="chat_name")
    recipient_id: Optional[int] = None
    type: Literal["group", "personal"] = Field(alias="chat_type")

    @model_validator(mode="after")
    def check_user_id_for_group_chat(self) -> Self:
        if self.check_group_condition():
            raise ValueError("For group chats, name must be specified, and recipient_id should be left empty")

        if self.check_personal_condition():
            raise ValueError("For personal chats, recipient_id must be specified, and name should be left empty")

        return self

    @property
    def is_group(self) -> bool:
        return self.type == ChatTypeEnum.group

    @property
    def is_personal(self) -> bool:
        return self.type == ChatTypeEnum.personal

    def check_group_condition(self) -> bool:
        return self.is_group and self.name is None

    def check_personal_condition(self) -> bool:
        return self.is_personal and self.recipient_id is None


class GroupChatCreate(BaseModel):
    name: str


class GroupChatJoin(BaseModel):
    chat_id: int
