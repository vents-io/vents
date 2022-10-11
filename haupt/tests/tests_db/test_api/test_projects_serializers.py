#!/usr/bin/python
#
# Copyright 2018-2022 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

import pytest

from haupt.db.api.projects.serializers import (
    ProjectDetailSerializer,
    ProjectNameSerializer,
    ProjectSerializer,
)
from tests.tests_db.test_api.base import BaseTestProjectSerializer


@pytest.mark.serializers_mark
class TestProjectNameSerializer(BaseTestProjectSerializer):
    serializer_class = ProjectNameSerializer
    expected_keys = {"name"}

    def test_serialize_one(self):
        obj1 = self.create_one()
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        for k, v in data.items():
            assert getattr(obj1, k) == v


@pytest.mark.serializers_mark
class TestProjectSerializer(BaseTestProjectSerializer):
    serializer_class = ProjectSerializer
    expected_keys = {
        "uuid",
        "name",
        "description",
        "tags",
        "created_at",
        "updated_at",
    }

    def test_serialize_one(self):
        obj1 = self.create_one()
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        data.pop("created_at")
        data.pop("updated_at")
        assert data.pop("uuid") == obj1.uuid.hex

        for k, v in data.items():
            assert getattr(obj1, k) == v


@pytest.mark.serializers_mark
class TestProjectDetailSerializer(TestProjectSerializer):
    serializer_class = ProjectDetailSerializer
    expected_keys = TestProjectSerializer.expected_keys | {
        "readme",
        "live_state",
    }

    def test_serialize_one(self):
        obj1 = self.create_one()
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        data.pop("created_at")
        data.pop("updated_at")
        assert data.pop("uuid") == obj1.uuid.hex

        for k, v in data.items():
            assert getattr(obj1, k) == v


del BaseTestProjectSerializer
