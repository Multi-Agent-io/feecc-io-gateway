from fastapi import HTTPException, status, Request

from database import MongoDbWrapper
from models import Employee
from shared.Config import Config


async def authenticate(request: Request) -> Employee:
    try:
        rfid_card_id: str = request.headers.get("rfid_card_id")
        user: Employee = await MongoDbWrapper().get_concrete_employee(rfid_card_id)

        if user.rfid_card_id == "1111111111" and Config().global_config["api_server"]["production_environment"]:
            raise ValueError("Development credentials are not allowed in production environment")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )

    return user
