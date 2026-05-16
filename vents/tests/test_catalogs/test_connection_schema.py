from unittest import TestCase

from clipped.compact.pydantic import ValidationError
from vents.connections.connection_schema import (
    BucketConnection,
    ClaimConnection,
    GitConnection,
    HostConnection,
    HostPathConnection,
)


class TestBucketConnection(TestCase):
    def test_claim_connect_config(self):
        config_dict = {}
        with self.assertRaises(ValidationError):
            BucketConnection.from_dict(config_dict)

        config_dict = {"bucket": "sdf"}
        config = BucketConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict


class TestClaimConnection(TestCase):
    def test_claim_connect_config(self):
        config_dict = {}
        with self.assertRaises(ValidationError):
            ClaimConnection.from_dict(config_dict)

        config_dict = {"volumeClaim": "foo"}
        with self.assertRaises(ValidationError):
            ClaimConnection.from_dict(config_dict)

        config_dict = {"volumeClaim": "foo", "mountPath": "foo", "readOnly": True}
        config = ClaimConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict


class TestHostPathConnection(TestCase):
    def test_host_path_connect_config(self):
        config_dict = {}
        with self.assertRaises(ValidationError):
            HostPathConnection.from_dict(config_dict)

        config_dict = {"host_path": "foo"}
        with self.assertRaises(ValidationError):
            HostPathConnection.from_dict(config_dict)

        config_dict = {"hostPath": "foo", "mountPath": "foo", "readOnly": True}
        config = HostPathConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict


class TestHostConnection(TestCase):
    def test_host_connect_config(self):
        config_dict = {}
        with self.assertRaises(ValidationError):
            HostConnection.from_dict(config_dict)

        config_dict = {"url": "foo", "insecure": True}
        config = HostConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict


class TestGitConnection(TestCase):
    def test_git_connect_config(self):
        config_dict = {}
        GitConnection.from_dict(config_dict)

        config_dict = {"url": "foo"}
        config = GitConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict

        config_dict = {"url": "foo", "revision": "foo"}
        config = GitConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict

        config_dict = {
            "url": "foo",
            "revision": "foo",
            "flags": ["flag1", "--flag2", "k=v"],
        }
        config = GitConnection.from_dict(config_dict)
        assert config.to_dict() == config_dict
