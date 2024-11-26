import json
import os
import tempfile

from unittest import TestCase

from vents.connections import ConnectionCatalog
from vents.connections.connection import Connection
from vents.settings import VENTS_CONFIG


class TestReader(TestCase):
    def setUp(self):
        # Clean up any test environment variables before each test
        self.cleanup_test_env()

    def tearDown(self):
        # Clean up after each test
        self.cleanup_test_env()

    def cleanup_test_env(self):
        test_vars = [
            "some_random_text_foo_000",
            "VENTS_some_random_text_foo_000",
            "test_key_1",
            "test_key_2",
            "VENTS_test_key_1",
            "VENTS_test_key_2",
        ]
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]

    def test_read_keys_from_env(self):
        assert VENTS_CONFIG.read_keys_from_env(keys=None) is None
        assert VENTS_CONFIG.read_keys_from_env(keys=[]) is None
        assert VENTS_CONFIG.read_keys_from_env(keys="some_random_text_foo_000") is None

        os.environ["some_random_text_foo_000"] = "a"
        assert VENTS_CONFIG.read_keys_from_env(["some_random_text_foo_000"]) == "a"

        os.environ["VENTS_some_random_text_foo_000"] = "a"
        assert VENTS_CONFIG.read_keys_from_env(["some_random_text_foo_000"]) == "a"

    def test_read_multiple_keys(self):
        # Test reading multiple keys
        os.environ["test_key_1"] = "value1"
        os.environ["test_key_2"] = "value2"

        result = VENTS_CONFIG.read_keys_from_env(["test_key_1", "test_key_2"])
        assert result == "value1"
        result = VENTS_CONFIG.read_keys_from_env(["test_key_2", "test_key_1"])
        assert result == "value2"

    def test_read_multiple_keys_with_prefix(self):
        # Test reading multiple keys with VENTS_ prefix
        os.environ["VENTS_test_key_1"] = "prefix_value1"
        os.environ["VENTS_test_key_2"] = "prefix_value2"

        result = VENTS_CONFIG.read_keys_from_env(["test_key_1", "test_key_2"])
        assert result == "prefix_value1"

    def test_mixed_prefix_priority(self):
        # Test that VENTS_ prefixed variables take priority
        os.environ["test_key_1"] = "normal_value"
        os.environ["VENTS_test_key_1"] = "prefixed_value"
        os.environ["VENTS_test_key_2"] = "prefixed_value_2"

        result = VENTS_CONFIG.read_keys_from_env(["test_key_1"])
        assert result == "normal_value"

        result = VENTS_CONFIG.read_keys_from_env(["test_key_2"])
        assert result == "prefixed_value_2"

    def test_missing_keys(self):
        # Test behavior when some keys are missing
        os.environ["test_key_1"] = "value1"

        result = VENTS_CONFIG.read_keys_from_env(["test_key_1", "nonexistent_key"])
        assert result == "value1"

        result = VENTS_CONFIG.read_keys_from_env(["nonexistent_key", "test_key_1"])
        assert result == "value1"

    def test_read_keys_from_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "test_key_1"), "w") as f:
                f.write("path_value1")
            with open(os.path.join(temp_dir, "test_bool"), "w") as f:
                f.write("true")

            # Test single key
            result = VENTS_CONFIG.read_keys_from_path([temp_dir], ["test_key_1"])
            assert result == "path_value1"

            # Test boolean value
            result = VENTS_CONFIG.read_keys_from_path([temp_dir], ["test_bool"])
            assert result is True

            # Test missing key
            result = VENTS_CONFIG.read_keys_from_path([temp_dir], ["nonexistent"])
            assert result is None

            # Test multiple paths (first path doesn't exist)
            result = VENTS_CONFIG.read_keys_from_path(
                ["/nonexistent/path", temp_dir], ["test_key_1"]
            )
            assert result == "path_value1"

    def test_read_keys_from_schema(self):
        schema = {
            "test_key_1": "schema_value1",
            "test_bool": "true",
            "test_bool_false": "false",
        }

        # Test single key
        result = VENTS_CONFIG.read_keys_from_schema(schema, ["test_key_1"])
        assert result == "schema_value1"

        # Test boolean values
        result = VENTS_CONFIG.read_keys_from_schema(schema, ["test_bool"])
        assert result is True
        result = VENTS_CONFIG.read_keys_from_schema(schema, ["test_bool_false"])
        assert result is False

        # Test missing key
        result = VENTS_CONFIG.read_keys_from_schema(schema, ["nonexistent"])
        assert result is None

        # Test empty schema
        result = VENTS_CONFIG.read_keys_from_schema({}, ["test_key_1"])
        assert result is None

    def test_connections_catalog(self):
        # Test get_connections_catalog_env_name
        expected_env_name = f"{VENTS_CONFIG.env_prefix}_CONNECTIONS_CATALOG"
        assert VENTS_CONFIG.get_connections_catalog_env_name() == expected_env_name

        # Test get_connections_catalog
        test_connection = Connection(name="test_conn", kind="http")
        catalog = VENTS_CONFIG.get_connections_catalog([test_connection])
        assert isinstance(catalog, ConnectionCatalog)
        assert catalog.connections_by_names["test_conn"] == test_connection

        # Test get_connection_for
        VENTS_CONFIG.set_connections_catalog([test_connection])
        retrieved_conn = VENTS_CONFIG.get_connection_for("test_conn")
        assert retrieved_conn == test_connection

        # Test get_connection_for with missing connection
        assert VENTS_CONFIG.get_connection_for("nonexistent") is None
        assert VENTS_CONFIG.get_connection_for(None) is None

    def test_load_connections_catalog(self):
        # Create a test catalog JSON
        test_catalog = {"connections": [{"name": "test_conn", "kind": "http"}]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as temp_file:
            json.dump(test_catalog, temp_file)
            temp_file.flush()

            # Set the environment variable
            os.environ[VENTS_CONFIG.get_connections_catalog_env_name()] = temp_file.name

            # Test loading catalog
            catalog = VENTS_CONFIG.load_connections_catalog()
            assert isinstance(catalog, ConnectionCatalog)
            assert "test_conn" in catalog.connections_by_names

        # Test with missing environment variable
        if VENTS_CONFIG.get_connections_catalog_env_name() in os.environ:
            del os.environ[VENTS_CONFIG.get_connections_catalog_env_name()]
        assert VENTS_CONFIG.load_connections_catalog() is None

    def test_read_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            with open(os.path.join(temp_dir, "TEST_KEY_1"), "w") as f:
                f.write("path_value1")

            # Test reading from path first
            result = VENTS_CONFIG.read_keys(
                context_paths=[temp_dir], keys=["test_key_1"]
            )
            assert result == "path_value1"

            # Test falling back to environment
            os.environ["TEST_KEY_2"] = "env_value2"
            result = VENTS_CONFIG.read_keys(
                context_paths=[temp_dir], keys=["test_key_2"]
            )
            assert result == "env_value2"

            # Test case insensitivity
            result = VENTS_CONFIG.read_keys(
                context_paths=[temp_dir], keys=["TEST_KEY_1"]
            )
            assert result == "path_value1"

            # Test with no underscore
            result = VENTS_CONFIG.read_keys(context_paths=[temp_dir], keys=["testkey1"])
            assert result is None
