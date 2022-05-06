"""Production Public Class Interfaces"""
from .board_log import BoardLog as __sl
from .cn0511_prod import TextInfo as __s

class BoardLog(__sl):
    pass

class TextInfo(__s):
    pass