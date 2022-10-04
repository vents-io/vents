#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from rest_framework import status

from django.core.handlers.asgi import ASGIRequest
from django.db import transaction
from django.http import HttpResponse
from django.urls import path

from polyaxon import settings
from polyaxon.k8s.async_manager import AsyncK8SManager
from polyaxon.utils.fqn_utils import get_resource_name_for_kind
from streams.controllers.k8s_check import k8s_check, reverse_k8s
from streams.controllers.k8s_crd import get_k8s_operation
from streams.controllers.k8s_pods import get_pods
from streams.endpoints.base import UJSONResponse


@transaction.non_atomic_requests
async def k8s_auth(request: ASGIRequest) -> HttpResponse:
    uri = request.headers.get("x-origin-uri")
    if not uri:
        return HttpResponse(
            content="This endpoint can only be a sub-requested.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        path, params = k8s_check(uri)
    except ValueError as e:
        return HttpResponse(
            content="Error validating path. {}".format(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return await reverse_k8s(path="{}?{}".format(path, params))


@transaction.non_atomic_requests
async def k8s_inspect(request: ASGIRequest, run_uuid: str) -> HttpResponse:
    resource_name = get_resource_name_for_kind(run_uuid=run_uuid)
    k8s_manager = AsyncK8SManager(
        namespace=settings.CLIENT_CONFIG.namespace,
        in_cluster=settings.CLIENT_CONFIG.in_cluster,
    )
    await k8s_manager.setup()
    k8s_operation = await get_k8s_operation(
        k8s_manager=k8s_manager, resource_name=resource_name
    )
    data = None
    if k8s_operation:
        data = await get_pods(k8s_manager=k8s_manager, run_uuid=run_uuid)
    if k8s_manager:
        await k8s_manager.close()
    return UJSONResponse(data or {})


URLS_RUNS_K8S_AUTH = "k8s/auth/"
URLS_RUNS_K8S_INSPECT = (
    "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/k8s_inspect"
)

# fmt: off
k8s_routes = [
    path(
        URLS_RUNS_K8S_AUTH,
        k8s_auth,
        # name="k8s",
        # methods=["GET"],
    ),
    path(
        URLS_RUNS_K8S_INSPECT,
        k8s_inspect,
        # name="k8s",
        # methods=["GET"],
    ),
]