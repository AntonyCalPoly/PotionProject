import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        green_potions_available = connection.execute(sqlalchemy.text("SELECT sku,num_potions,cost FROM global_inventory WHERE sku = 'GREEN_POTION_0';")).fetchone()
        
        red_potions_available = connection.execute(sqlalchemy.text("SELECT sku,num_potions,cost FROM global_inventory WHERE sku = 'RED_POTION_0';")).fetchone()

        blue_potions_available = connection.execute(sqlalchemy.text("SELECT sku,num_potions,cost FROM global_inventory WHERE sku = 'BLUE_POTION_0';")).fetchone()

    if green_potions_available.num_potions > 0:
         return [
                {
                    "sku": green_potions_available.sku,
                    "name": "green potion",
                    "quantity": green_potions_available.num_potions,
                    "price": green_potions_available.cost,
                    "potion_type": [0, 100, 0, 0],
                }
        ]
    if red_potions_available.num_potions > 0:
         return [
                {
                    "sku": red_potions_available.sku,
                    "name": "red potion",
                    "quantity": red_potions_available.num_potions,
                    "price": red_potions_available.cost,
                    "potion_type": [100, 0, 0, 0],
                }
        ]
    if blue_potions_available.num_potions > 0:
         return [
                {
                    "sku": blue_potions_available.sku,
                    "name": "blue potion",
                    "quantity": blue_potions_available.num_potions,
                    "price": blue_potions_available.cost,
                    "potion_type": [0, 0, 100, 0],
                }
        ]
