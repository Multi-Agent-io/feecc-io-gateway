from .. import test_client, pytest_plugins
import os

test_filename = "ipfs_test.txt"


def test_ipfs_push_nothing() -> None:
    resp = test_client.post("/io-gateway/ipfs")
    assert resp.status_code != 200, "/ipfs accepted literally nothing"


def test_ipfs_push_invalid_path() -> None:
    req_data = {"filename": "wrong_file.name"}
    resp = test_client.post("/io-gateway/ipfs", json=req_data)
    assert resp.ok
    assert resp.status_code != 200, "Gateway accepted invalid path"


def test_ipfs_push_valid_path() -> None:
    with open(test_filename, "w") as f:
        f.write("test file")
    req_data = {"filename": test_filename}
    resp = test_client.post("/io-gateway/ipfs", json=req_data)
    if not os.path.exists(test_filename):
        raise ValueError("Unable to create or delete file")
    os.remove(test_filename)
    assert resp.ok
    assert resp.status_code == 200, f"File wasn't sent: {resp.json()}"


def test_pinata_push_nothing() -> None:
    resp = test_client.post("/io-gateway/pinata")
    assert resp.status_code != 200, "/pinata accepted literally nothing"


def test_pinata_push_invalid_path() -> None:
    req_data = {"filename": "wrong_file.name"}
    resp = test_client.post("/io-gateway/pinata", json=req_data)
    assert resp.ok
    assert resp.status_code != 200, "Gateway accepted invalid path"


def test_pinata_push_valid_path() -> None:
    with open(test_filename, "w") as f:
        f.write("test file")
    req_data = {"filename": test_filename}
    resp = test_client.post("/io-gateway/pinata", json=req_data)
    if not os.path.exists(test_filename):
        raise ValueError("Unable to create or delete file")
    os.remove(test_filename)
    assert resp.ok
    assert resp.status_code == 200, f"File wasn't sent: {resp.json()}"
