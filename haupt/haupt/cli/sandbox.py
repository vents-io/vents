#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
import os

import click


def start_sandbox(
    host: str, port: int, workers: int, per_core: bool, path: str, uds: str
):
    """Start sandbox service."""
    from haupt.cli.runners.sandbox import start
    from polyaxon.env_vars.keys import EV_KEYS_SANDBOX_ROOT, EV_KEYS_SERVICE
    from polyaxon.services.values import PolyaxonServices

    os.environ[EV_KEYS_SERVICE] = PolyaxonServices.SANDBOX
    if path:
        os.environ[EV_KEYS_SANDBOX_ROOT] = path

    start(host=host, port=port, workers=workers, per_core=per_core, uds=uds)


@click.command()
@click.option(
    "--host",
    help="The service host.",
)
@click.option(
    "--port",
    type=int,
    help="The service port.",
)
@click.option(
    "--workers",
    type=int,
    help="Number of workers.",
)
@click.option(
    "--per-core",
    is_flag=True,
    default=False,
    help="To enable workers per core.",
)
@click.option(
    "--path",
    help="The service host.",
)
@click.option(
    "--uds",
    help="UNIX domain socket binding.",
)
def sandbox(host: str, port: int, workers: int, per_core: bool, path: str, uds: str):
    """Start a new sandbox session.

    This command is available starting from v1.18.
    """
    return start_sandbox(
        host=host, port=port, workers=workers, per_core=per_core, path=path, uds=uds
    )
