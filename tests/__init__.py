from fastapi.testclient import TestClient
import app

test_client = TestClient(app.app)

pytest_plugins = ["docker_compose"]
