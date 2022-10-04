#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from common.events.registry import run
from db import executor

executor.subscribe(run.RunCreatedEvent)
executor.subscribe(run.RunResumedActorEvent)
executor.subscribe(run.RunStoppedActorEvent)
executor.subscribe(run.RunApprovedActorEvent)
executor.subscribe(run.RunNewStatusEvent)
executor.subscribe(run.RunDoneEvent)
executor.subscribe(run.RunDeletedActorEvent)
executor.subscribe(run.RunNewArtifactsEvent)