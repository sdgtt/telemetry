from enum import Enum, unique

@unique
class BoardStatus(Enum):
    POWER_ON = 1
    UBOOT_READY = 2
    LINUX_READY = 3
    POWER_OFF = 4
    DEACTIVATED = 5
