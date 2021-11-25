import pytest

from .. import test_client


def test_server_running():
    response = test_client.get("/")
    assert response.json() == {"detail": "Not Found"}
