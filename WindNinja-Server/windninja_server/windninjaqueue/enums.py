from enum import Enum


class QueueMode(Enum):
    disabled = 0
    immediate = 1  # deprecated
    enabled = 2


class QueueStatus(Enum):
    unknown = 0
    pending = 1
    running = 2
    complete = 3
    failed = 4
