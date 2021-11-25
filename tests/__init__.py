from fastapi.testclient import TestClient
import app

test_client = TestClient(app.app)
