import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    
    potions = [
        {"sku": "GREEN_POTION_0", "name": "green potion", "potion_type": [0, 100, 0, 0]},
        {"sku": "RED_POTION_0", "name": "red potion", "potion_type": [100, 0, 0, 0]},
        {"sku": "BLUE_POTION_0", "name": "blue potion", "potion_type": [0, 0, 100, 0]},
    ]

    with db.engine.begin() as connection:
        potion_skus = [potion['sku'] for potion in potions]
        potion_data = connection.execute(
            sqlalchemy.text("SELECT sku, num_potions, cost FROM global_inventory WHERE sku = ANY(:sku_list)"),
            {"sku_list": potion_skus}
        ).fetchall()

    available_potions = {entry.sku: entry for entry in potion_data}

    for potion in potions:
        available = available_potions.get(potion["sku"])
        if available and available.num_potions > 0:
            return [{
                "sku": available.sku,
                "name": potion["name"],
                "quantity": available.num_potions,
                "price": available.cost,
                "potion_type": potion["potion_type"],
            }]

    return []
