from functools import reduce
from telegram import Update
from telegram.ext import Filters, BaseFilter
from ..dict_enum import DictEnum
from .trigger_result import TriggerResult
from .basic_triggers import BaseTrigger
from ..users_helper import DEFAULT_USERS_HELPER


class FilterBasedTrigger(BaseTrigger):
    def __init__(self, message_filter: BaseFilter):
        super().__init__()
        self.filter = message_filter

    def check_trigger(self, update: Update) -> TriggerResult:
        return TriggerResult(should_respond=self.filter(update.message))


class _UserFilterBasedTrigger(FilterBasedTrigger):
    def __init__(self, nickname=None, user_id=None, username=None):
        if nickname is not None:
            super().__init__(Filters.user(DEFAULT_USERS_HELPER.get_user_id_by_nickname(nickname)))
        else:
            super().__init__(Filters.user(user_id, username))


class _ChatFilterBasedTrigger(FilterBasedTrigger):
    def __init__(self, chat_id=None, username=None):
        super().__init__(Filters.chat(chat_id, username))


class _LanguageFilterBasedTrigger(FilterBasedTrigger):
    def __init__(self, lang):
        super().__init__(Filters.language(lang))


class _MessageTypeFilterBasedTrigger(FilterBasedTrigger):
    def __init__(self, message_type):
        subfilters = message_type.split('.')
        try:
            message_type_filter = reduce(getattr, subfilters, Filters)
            if isinstance(message_type_filter, BaseFilter):
                super().__init__(message_type_filter)
            else:
                raise ValueError(f'"{message_type}" is not a valid message type to filter by, '
                                 f'but it is a valid filter. Did you mean to use '
                                 f'"{message_type}" as a filter type instead?')
        except AttributeError:
            raise ValueError(f'"{message_type}" is not a valid message type to filter by.')


class FilterTriggers(DictEnum):
    message_type = _MessageTypeFilterBasedTrigger
    user = _UserFilterBasedTrigger
    chat = _ChatFilterBasedTrigger
    language = _LanguageFilterBasedTrigger
