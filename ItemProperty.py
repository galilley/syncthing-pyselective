# -*- coding: utf-8 -*-

import enum


class SyncState(enum.Enum):
    unknown = -1
    syncing = 0
    ignored = 1
    newlocal = 2
    conflict = 3


class Type(enum.Enum):
    FILE = 0
    DIRECTORY = 1

    # SyncThing aliases
    FILE_INFO_TYPE_FILE = 0
    FILE_INFO_TYPE_DIRECTORY = 1


class ItemProperty:
    def __init__(self):
        pass
