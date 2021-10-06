from fastapi import HTTPException, Header, status

from .database import MongoDbWrapper
from .models import Employee
from .shared.config import config


async def authenticate(rfid_card_id: str = Header(...)) -> Employee:
    try:
        if rfid_card_id == "1111111111" and config.api_server.production_environment:
            raise ValueError("Development credentials are not allowed in production environment")

        return await MongoDbWrapper().get_concrete_employee(rfid_card_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )
