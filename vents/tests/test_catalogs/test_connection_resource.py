from unittest import TestCase

from clipped.compact.pydantic import ValidationError
from clipped.utils.assertions import assert_equal_dict
from vents.connections.connection_resource import ConnectionResource


class TestConnectionResource(TestCase):
    def test_resource_config(self):
        config_dict = {}
        with self.assertRaises(ValidationError):
            ConnectionResource.from_dict(config_dict)

        config_dict = {"name": "foo"}
        config = ConnectionResource.from_dict(config_dict)
        assert_equal_dict(config.to_dict(), config_dict)

        config_dict = {"name": "foo", "mount_path": 213}
        with self.assertRaises(ValidationError):
            ConnectionResource.from_dict(config_dict)

        config_dict = {"name": "foo", "items": 213}
        with self.assertRaises(ValidationError):
            ConnectionResource.from_dict(config_dict)

        config_dict = {
            "name": "foo",
            "mountPath": "/foo/path",
            "items": ["item1", "item2"],
        }
        config = ConnectionResource.from_dict(config_dict)
        assert_equal_dict(config.to_dict(), config_dict)

        config_dict = {"name": "foo", "items": ["item1", "item2"]}
        config = ConnectionResource.from_dict(config_dict)
        assert_equal_dict(config.to_dict(), config_dict)

        config_dict = {
            "name": "sdf",
            "items": ["foo"],
            "mountPath": "/bar",
            "hostPath": "/tmp/other_path",
        }
        config = ConnectionResource.from_dict(config_dict)
        assert config.to_dict() == config_dict

    def test_resource_instance(self):
        config = ConnectionResource(name="test")
        assert config.to_dict() == {"name": "test"}

        config = ConnectionResource(name="test", is_requested=True)
        assert config.to_dict() == {"name": "test", "isRequested": True}

        config = ConnectionResource(name="test", is_requested=False)
        assert config.to_dict() == {"name": "test", "isRequested": False}

        config = ConnectionResource(
            name="test",
            items=["item"],
            mount_path="/some_path",
        )
        assert config.to_dict() == {
            "name": "test",
            "items": ["item"],
            "mountPath": "/some_path",
        }

        config = ConnectionResource(
            name="test",
            mount_path="/some_path",
            host_path="/tmp/other_path",
            is_requested=True,
        )
        assert config.to_dict() == {
            "name": "test",
            "mountPath": "/some_path",
            "hostPath": "/tmp/other_path",
            "isRequested": True,
        }
