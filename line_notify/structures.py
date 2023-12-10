from dataclasses import dataclass
from enum import Enum, auto


class DisasterTextType(Enum):
    CURERNT = auto()
    PAST = auto()
    PAST_WITH_TIME = auto()


@dataclass
class DisasterTextInfo:
    disaster_text: str
    disaster_text_type: DisasterTextType
