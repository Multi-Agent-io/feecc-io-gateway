import os

import pytest
import os
import requests

from .. import test_client


@pytest.fixture
def test_img() -> str:
    test_picture = "test_img.png"
    if not os.path.exists(test_picture):
        robonomics_logo = "https://upload.wikimedia.org/wikipedia/commons/3/3d/Dvach_logo.png"
        logo = requests.get(robonomics_logo)
        with open(test_picture, "wb") as f:
            f.write(logo.content)
    return test_picture


@pytest.mark.printer
def test_print_image(test_img) -> None:
    """FIXME: check behaviour"""
    resp = test_client.post("/printing/print_image", files={"image_file": open(test_img, "rb")})
    assert resp.ok
    assert resp.json().get("status") == 200


@pytest.mark.printer
def test_print_image_annotated(test_img) -> None:
    resp = test_client.post(
        "/printing/print_image",
        files={"image_file": open(test_img, "rb")},
        data={"annotation": "image with annotation"},
    )
    assert resp.ok
    assert resp.json().get("status") == 200
