#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from django.conf import settings

from haupt.common.options import option_namespaces, option_subjects
from haupt.common.options.cache import LONG_CACHE_TTL
from haupt.common.options.option import (
    NAMESPACE_DB_OPTION_MARKER,
    Option,
    OptionScope,
    OptionStores,
)
from polyaxon import types

STATS_DEFAULT_PREFIX = "{}{}{}".format(
    option_namespaces.STATS, NAMESPACE_DB_OPTION_MARKER, option_subjects.DEFAULT_PREFIX
)

OPTIONS = {STATS_DEFAULT_PREFIX}


class StatsDefaultPrefix(Option):
    key = STATS_DEFAULT_PREFIX
    scope = OptionScope.GLOBAL
    is_secret = False
    is_optional = True
    is_list = False
    typing = types.STR
    store = OptionStores(settings.STORE_OPTION)
    default = None
    options = None
    cache_ttl = LONG_CACHE_TTL
