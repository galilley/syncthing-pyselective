# -*- coding: utf-8 -*-

import enum


class SyncState(enum.Enum):
    unknown = -1
    syncing = 0
    ignored = 1
    newlocal = 2
    conflict = 3

class ItemProperty:
    def __init__(self):
        pass
