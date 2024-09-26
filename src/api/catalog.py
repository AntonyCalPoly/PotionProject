import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
   with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    """
    Each unique item combination must have only a single price.
    """

    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": quantity[0],
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]
