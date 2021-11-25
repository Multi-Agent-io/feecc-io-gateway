from .. import test_client
import os

test_filename = "ipfs_test.txt"


def test_ipfs_push_nothing() -> None:
    resp = test_client.post("/io-gateway/publish-to-ipfs/by-path")
    assert resp.status_code != 200, "/ipfs accepted literally nothing"


def test_ipfs_push_invalid_path() -> None:
    req_data = {"absolute_path": os.path.abspath("wrong_file.name")}
    resp = test_client.post("/io-gateway/publish-to-ipfs/by-path", json=req_data)
    assert resp.status_code == 404, "Gateway accepted invalid path"


def test_ipfs_push_valid_path() -> None:
    with open(test_filename, "w") as f:
        f.write("test file")
    req_data = {"absolute_path": os.path.abspath(test_filename)}
    resp = test_client.post("/io-gateway/publish-to-ipfs/by-path", json=req_data)
    if not os.path.exists(test_filename):
        raise ValueError("Unable to create or delete file")
    os.remove(test_filename)
    assert resp.ok
    assert resp.status_code == 200, f"File wasn't sent: {resp.json()}"
