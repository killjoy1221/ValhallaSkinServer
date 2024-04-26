import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import boto3
import pytest
from moto import mock_aws

from valhalla.files import get_filesystem


@pytest.fixture(scope="function")
def aws_credentials() -> None:
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def aws(aws_credentials: None) -> Generator[None, Any, None]:
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def s3_filesystem(aws: None) -> str:
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="bucket.com")
    return "s3://bucket.com/path"


@pytest.fixture(scope="function")
def local_filesystem(tmpdir: Path) -> str:
    return f"file:///{tmpdir}"


@pytest.mark.parametrize(
    "url",
    [
        "local_filesystem",
        "s3_filesystem",
    ],
)
def test_filesystem(url: str, request: pytest.FixtureRequest) -> None:
    url = request.getfixturevalue(url)
    fs = get_filesystem(url)
    file = fs / "file.txt"
    assert not file.exists()

    file.write_bytes(b"hello, world")

    assert file.exists()
