# -*- coding: utf-8 -*-
from datetime import datetime

_utcnow = datetime.utcnow


def utcnow():
    """
    Patchable utcnow

    Patch by replacing _utcnow(), useful for unittests

    """
    dt = _utcnow()
    return dt
