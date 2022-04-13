import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .models import Employee
from .shared.config import config
from .shared.Singleton import SingletonMeta


def _get_database_name(db_uri: str) -> str:
    """Get DB name in cluster from a MongoDB connection url"""
    db_name: str = db_uri.split("/")[-1]

    if "?" in db_name:
        db_name = db_name.split("?")[0]

    return db_name


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client_url: str = config.mongo_db.mongo_connection_url
        mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_client_url)

        db_name: str = _get_database_name(mongo_client_url)
        self._database = mongo_client[db_name]
        self._employee_collection: AsyncIOMotorCollection = self._database["employeeData"]

        logger.info("Connected to MongoDB")

    @staticmethod
    async def _get_element_by_key(collection_: AsyncIOMotorCollection, key: str, value: str) -> tp.Dict[str, tp.Any]:
        result: tp.Dict[str, tp.Any] = await collection_.find_one({key: value}, {"_id": 0})

        if not result:
            raise ValueError(f"No results found for query '{key}:{value}'")

        return result

    async def get_concrete_employee(self, card_id: str) -> Employee:
        try:
            employee_data = await self._get_element_by_key(self._employee_collection, key="rfid_card_id", value=card_id)
        except ValueError:
            raise ValueError(f"Employee with card id {card_id} not found")

        return Employee(
            name=employee_data["name"], position=employee_data["position"], rfid_card_id=employee_data["rfid_card_id"]
        )
