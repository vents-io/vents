#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
from typing import Union

from rest_framework import status

from django.core.handlers.asgi import ASGIRequest
from django.db import transaction
from django.http import FileResponse, HttpResponse
from django.urls import path

from common.endpoints.files import FilePathResponse
from polyaxon.fs.async_manager import (
    check_is_file,
    delete_file_or_dir,
    download_dir,
    download_file,
    list_files,
)
from polyaxon.utils.bool_utils import to_bool
from streams.connections.fs import AppFS
from streams.controllers.notebooks import render_notebook
from streams.controllers.uploads import handle_upload
from streams.endpoints.base import UJSONResponse
from streams.endpoints.utils import redirect_file


def clean_path(filepath: str):
    return filepath.strip("/")


@transaction.non_atomic_requests
async def handle_artifact(
    request: ASGIRequest, namespace: str, owner: str, project: str, run_uuid: str
) -> HttpResponse:
    if request.method == "GET":
        return await download_artifact(request, run_uuid=run_uuid)
    if request.method == "DELETE":
        return await delete_artifact(request, run_uuid=run_uuid)
    if request.method == "POST":
        return await upload_artifact(request)


@transaction.non_atomic_requests
async def ro_artifact(
    request: ASGIRequest,
    namespace: str,
    owner: str,
    project: str,
    run_uuid: str,
    path: str,
) -> HttpResponse:
    return await download_artifact(request, run_uuid, path, True)


async def download_artifact(
    request: ASGIRequest, run_uuid: str, path: str = None, stream: bool = None
) -> Union[HttpResponse, FileResponse]:
    filepath = request.GET.get("path", path or "")
    stream = to_bool(request.GET.get("stream", stream), handle_none=True)
    force = to_bool(request.GET.get("force"), handle_none=True)
    render = to_bool(request.GET.get("render"), handle_none=True)
    if not filepath:
        return HttpResponse(
            content="A `path` query param is required to stream a file content",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if render and not filepath.endswith(".ipynb"):
        return HttpResponse(
            content="Artifact with 'filepath={}' does not have a valid extension.".format(
                filepath
            ),
            status=status.HTTP_400_BAD_REQUEST,
        )
    subpath = "{}/{}".format(run_uuid, clean_path(filepath)).rstrip("/")
    archived_path = await download_file(
        fs=await AppFS.get_fs(), subpath=subpath, check_cache=not force
    )
    if not archived_path:
        return HttpResponse(
            content="Artifact not found: filepath={}".format(archived_path),
            status=status.HTTP_404_NOT_FOUND,
        )
    if stream:
        if render:
            archived_path = await render_notebook(
                archived_path=archived_path, check_cache=not force
            )
        return FilePathResponse(filepath=archived_path)
    return await redirect_file(archived_path)


async def upload_artifact(request: ASGIRequest) -> HttpResponse:
    return await handle_upload(fs=await AppFS.get_fs(), request=request, is_file=True)


async def delete_artifact(request: ASGIRequest, run_uuid: str) -> HttpResponse:
    filepath = request.GET.get("path", "")
    if not filepath:
        return HttpResponse(
            content="A `path` query param is required to delete a file",
            status=status.HTTP_400_BAD_REQUEST,
        )
    subpath = "{}/{}".format(run_uuid, clean_path(filepath)).rstrip("/")
    is_deleted = await delete_file_or_dir(
        fs=await AppFS.get_fs(), subpath=subpath, is_file=True
    )
    if not is_deleted:
        return HttpResponse(
            content="Artifact could not be deleted: filepath={}".format(subpath),
            status=status.HTTP_400_BAD_REQUEST,
        )
    return HttpResponse(
        status=status.HTTP_204_NO_CONTENT,
    )


@transaction.non_atomic_requests
async def handle_artifacts(
    request: ASGIRequest, namespace: str, owner: str, project: str, run_uuid: str
) -> HttpResponse:
    if request.method == "GET":
        return await download_artifacts(request, run_uuid=run_uuid)
    if request.method == "DELETE":
        return await delete_artifacts(request, run_uuid=run_uuid)
    if request.method == "POST":
        return await upload_artifacts(request)


async def download_artifacts(request: ASGIRequest, run_uuid: str) -> HttpResponse:
    check_path = to_bool(request.GET.get("check_path"), handle_none=True)
    if not check_path:
        # Backwards compatibility
        check_path = to_bool(request.GET.get("check_file"), handle_none=True)
    path = request.GET.get("path", "")
    subpath = "{}/{}".format(run_uuid, clean_path(path)).rstrip("/")
    fs = await AppFS.get_fs()
    if check_path:
        is_file = await check_is_file(fs=fs, subpath=subpath)
        if is_file:
            return await download_artifact(request, run_uuid=run_uuid)
    archived_path = await download_dir(fs=fs, subpath=subpath, to_tar=True)
    if not archived_path:
        return HttpResponse(
            content="Artifact not found: filepath={}".format(archived_path),
            status=status.HTTP_404_NOT_FOUND,
        )
    return await redirect_file(archived_path)


async def upload_artifacts(request: ASGIRequest) -> HttpResponse:
    return await handle_upload(fs=await AppFS.get_fs(), request=request, is_file=False)


async def delete_artifacts(request: ASGIRequest, run_uuid: str) -> HttpResponse:
    path = request.GET.get("path", "")
    subpath = "{}/{}".format(run_uuid, clean_path(path)).rstrip("/")
    is_deleted = await delete_file_or_dir(
        fs=await AppFS.get_fs(), subpath=subpath, is_file=False
    )
    if not is_deleted:
        return HttpResponse(
            content="Artifacts could not be deleted: filepath={}".format(subpath),
            status=status.HTTP_400_BAD_REQUEST,
        )
    return HttpResponse(
        status=status.HTTP_204_NO_CONTENT,
    )


@transaction.non_atomic_requests
async def tree_artifacts(
    request: ASGIRequest, namespace: str, owner: str, project: str, run_uuid: str
) -> UJSONResponse:
    filepath = request.GET.get("path", "")
    ls = await list_files(
        fs=await AppFS.get_fs(),
        subpath=run_uuid,
        filepath=clean_path(filepath),
        force=True,
    )
    return UJSONResponse(ls)


URLS_RUNS_ARTIFACT = (
    "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/artifact"
)
URLS_RUNS_EMBEDDED_ARTIFACT = (
    "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/embedded_artifact"
)
URLS_RUNS_RO_ARTIFACT = "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/ro_artifact/{path:path}"
URLS_RUNS_ARTIFACTS = (
    "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/artifacts"
)
URLS_RUNS_ARTIFACTS_TREE = (
    "<str:namespace>/<str:owner>/<str:project>/runs/<str:run_uuid>/artifacts/tree"
)

# fmt: off
artifacts_routes = [
    path(
        URLS_RUNS_ARTIFACT,
        handle_artifact,
        # name="download_artifact",
        # methods=["GET", "DELETE", "POST"],
    ),
    path(
        URLS_RUNS_EMBEDDED_ARTIFACT,
        handle_artifact,
        # name="download_embedded_artifact",
        # methods=["GET"],
    ),
    path(
        URLS_RUNS_RO_ARTIFACT,
        ro_artifact,
        # name="read_only_artifact",
        # methods=["GET"],
    ),
    path(
        URLS_RUNS_ARTIFACTS,
        handle_artifacts,
        # name="download_artifacts",
        # methods=["GET", "DELETE", "POST"],
    ),
    path(
        URLS_RUNS_ARTIFACTS_TREE,
        tree_artifacts,
        # name="list_artifacts",
        # methods=["GET"],
    ),
]