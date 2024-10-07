import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    mixed_potions = {
        'GREEN_POTION_0': 0,
        'RED_POTION_0': 0,
        'BLUE_POTION_0': 0
    }

    for potion in potions_delivered:
        if potion.potion_type[1] == 100:
            mixed_potions['GREEN_POTION_0'] += potion.quantity
        if potion.potion_type[0] == 100:
            mixed_potions['RED_POTION_0'] += potion.quantity
        if potion.potion_type[2] == 100:
            mixed_potions['BLUE_POTION_0'] += potion.quantity

    with db.engine.begin() as connection:
        for sku, quantity in mixed_potions.items():
            if quantity > 0:
                connection.execute(sqlalchemy.text(f"""
                    UPDATE global_inventory 
                    SET num_potions = num_potions + :quantity, 
                        num_ml = num_ml - :ml_decrement 
                    WHERE sku = :sku
                """), {
                    'quantity': quantity,
                    'ml_decrement': quantity * 100,
                    'sku': sku
                })
                
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    bottler_plan = []

    ml_quantities = {}

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        ml_quantity = connection.execute(sqlalchemy.text("SELECT sku, num_ml FROM global_inventory")).fetchall()

    for entry in ml_quantity:
        ml_quantities[entry.sku] = entry.num_ml

    potion_types = {
        "GREEN_POTION_0": ml_quantities.get("GREEN_POTION_0", 0) // 100,
        "RED_POTION_0": ml_quantities.get("RED_POTION_0", 0) // 100,
        "BLUE_POTION_0": ml_quantities.get("BLUE_POTION_0", 0) // 100
    }

    for potion_sku, quantity in potion_types.items():
        if quantity > 0:
            if potion_sku == "GREEN_POTION_0":
                potion_type = [0, 100, 0, 0]
            elif potion_sku == "RED_POTION_0":
                potion_type = [100, 0, 0, 0]
            elif potion_sku == "BLUE_POTION_0":
                potion_type = [0, 0, 100, 0]

            bottler_plan.append({
                "potion_type": potion_type,
                "quantity": quantity,
            })

    return bottler_plan

if __name__ == "__main__":
    print(get_bottle_plan())
