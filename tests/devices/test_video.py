import pytest

from .. import test_client, pytest_plugins


@pytest.mark.video
def test_get_video_cameras_list() -> None:
    resp = test_client.get("/video/cameras")
    assert resp.ok is True, resp.text
    assert resp.json().get("cameras", None) is not None, "No cameras found (check config)"


@pytest.mark.video
def test_get_video_records_list() -> None:
    resp = test_client.get("/video/records")
    assert resp.ok is True, resp.text
    assert resp.json().get("ongoing_records", None) is None, "when did we started recording?"
    assert resp.json().get("ended_records", None) is None, "when did we ended recording?"


@pytest.mark.video
def test_start_first_record() -> None:  # TODO
    resp = test_client.post("/video/camera/1/start")
    assert resp.ok is True, resp.text
    assert resp.status_code == 200, resp.json().get("details", None)



@pytest.mark.video
def test_stop_first_record() -> None:  # TODO
    pass


@pytest.mark.video
def test_stop_first_record_again() -> None:  # TODO
    pass


@pytest.mark.video
def test_start_second_record() -> None:  # TODO
    pass


@pytest.mark.video
def test_stop_first_and_second_record() -> None:  # TODO
    pass
