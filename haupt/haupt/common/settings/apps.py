#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from typing import Optional, Tuple

from common.config_manager import ConfigManager


def set_apps(
    context,
    config: ConfigManager,
    third_party_apps: Optional[Tuple],
    project_apps: Tuple,
    use_db_apps: bool = True,
    use_staticfiles_app: bool = True,
):

    extra_apps = config.get_string(
        "POLYAXON_EXTRA_APPS", is_list=True, is_optional=True
    )
    extra_apps = tuple(extra_apps) if extra_apps else ()

    apps = ()
    if use_db_apps:
        apps += (
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
        )

    if use_staticfiles_app:
        apps += ("django.contrib.staticfiles",)

    model_apps = ()
    if use_db_apps:
        if config.is_sqlite_db_engine:
            model_apps = ("db.sqlite.db.apps.DBConfig",)
        else:
            model_apps = ("db.pgsql.db.apps.DBConfig",)

    third_party_apps = third_party_apps or ()
    project_apps = project_apps or ()

    context["INSTALLED_APPS"] = (
        apps + third_party_apps + model_apps + extra_apps + project_apps
    )