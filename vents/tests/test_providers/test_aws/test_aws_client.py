import os

from unittest import TestCase

import boto3

from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from moto import mock_aws

from vents.providers.aws.service import AWSService


class TestAwsClient(TestCase):
    @mock_aws
    def test_get_aws_session(self):
        aws_service = AWSService(
            access_key_id="a1",
            secret_access_key="a2",
            session_token="a3",
            region="a4",
        )
        session = aws_service.session
        assert isinstance(session, boto3.session.Session)
        assert session.region_name == "a4"
        credentials = session.get_credentials()
        assert credentials.access_key == "a1"
        assert credentials.secret_key == "a2"
        assert credentials.token == "a3"

        os.environ["AWS_ACCESS_KEY_ID"] = "b1"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "b2"
        os.environ["AWS_SECURITY_TOKEN"] = "b3"
        os.environ["AWS_REGION"] = "b4"
        aws_service = AWSService.load_from_connection(connection=None)
        session = aws_service.session
        assert isinstance(session, boto3.session.Session)
        assert session.region_name == "b4"
        credentials = session.get_credentials()
        assert credentials.access_key == "b1"
        assert credentials.secret_key == "b2"
        assert credentials.token == "b3"

    @mock_aws
    def test_get_client(self):
        aws_service = AWSService(resource="s3")
        s3_client = aws_service.get_client()
        assert isinstance(s3_client, BaseClient)

    @mock_aws
    def test_get_resource(self):
        aws_service = AWSService(resource="s3")
        s3_resource = aws_service.get_resource()
        assert isinstance(s3_resource, ServiceResource)
