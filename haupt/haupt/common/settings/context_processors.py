#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from haupt import pkg
from haupt.common import conf
from haupt.common.options.registry.core import (
    UI_ASSETS_VERSION,
    UI_BASE_URL,
    UI_ENABLED,
    UI_OFFLINE,
)


def version(request):
    return {"version": pkg.VERSION}


def ui_base_url(request):
    return {"ui_base_url": conf.get(UI_BASE_URL)}


def ui_assets_version(request):
    return {
        "ui_assets_version": "{}.{}".format(pkg.VERSION, conf.get(UI_ASSETS_VERSION))
    }


def ui_offline(request):
    return {"ui_offline": conf.get(UI_OFFLINE)}


def ui_enabled(request):
    return {"ui_enabled": conf.get(UI_ENABLED)}
