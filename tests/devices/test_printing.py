import os

import pytest
import os
import requests

from .. import test_client, pytest_plugins


@pytest.fixture
def test_img() -> str:
    test_picture = "test_img.svg"
    if not os.path.exists(test_picture):
        robonomics_logo = "https://robonomics.network/assets/static/robonomics-logo.4520fc0.674fd3b96847876764f360539d019573.svg"
        logo = requests.get(robonomics_logo)
        with open(test_picture, "wb") as f:
            f.write(logo.content)
    return test_picture


@pytest.mark.printer
def test_print_image(test_img) -> None:
    """FIXME: check behaviour"""
    resp = test_client.post("/printing/print_image", files={"image_file": open(test_img, "rb")})
    assert resp.ok is True
    assert resp.status_code == 200


@pytest.mark.printer
def test_print_image_annotated(test_img) -> None:
    resp = test_client.post("/printing/print_image", files={"image_file": open(test_img, "rb")},
                            json={"annotation": "image with annotation"})
    assert resp.ok is True
    assert resp.status_code == 200
