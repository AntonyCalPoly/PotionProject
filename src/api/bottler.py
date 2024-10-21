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
    
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            custom_potions = connection.execute(sqlalchemy.text("SELECT id FROM custom_potions where percent_red = :red_ml AND percent_green = :green_ml AND percent_blue = :blue_ml AND percent_dark = :dark_ml;"),
                {
                "red_ml": potion.potion_type[0],
                "green_ml": potion.potion_type[1],
                "blue_ml": potion.potion_type[2],
                "dark_ml": potion.potion_type[3]
            }).fetchone()       

            if custom_potions:
                connection.execute(sqlalchemy.text("UPDATE custom_potions SET num_potions = num_potions + :quantity WHERE id = :id;"),
                    {"quantity": potion.quantity, "id": custom_potions.id})  

                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, green_ml = green_ml - :green_ml, blue_ml = blue_ml - :blue_ml, dark_ml = dark_ml - :dark_ml;"),
                    {
                    "red_ml": potion.potion_type[0] * potion.quantity,
                    "green_ml": potion.potion_type[1] * potion.quantity,
                    "blue_ml": potion.potion_type[2] * potion.quantity,
                    "dark_ml": potion.potion_type[3] * potion.quantity
                })                         

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        get_inventory = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml FROM global_inventory;")).fetchone()

        get_potions = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml, id FROM custom_potions;")).fetchone()

    bottler_plan = []

    red_ml_left = get_inventory.red_ml
    green_ml_left = get_inventory.green_ml
    blue_ml_left = get_inventory.blue_ml
    dark_ml_left = get_inventory.dark_ml
    
    
    for potion_type in get_potions:
        max_potions = min(
            red_ml_left // potion_type.red_ml if potion_type.red_ml > 0 else float('inf'),
            green_ml_left // potion_type.green_ml if potion_type.green_ml > 0 else float('inf'),
            blue_ml_left // potion_type.blue_ml if potion_type.blue_ml > 0 else float('inf'),
            dark_ml_left // potion_type.dark_ml if potion_type.dark_ml > 0 else float('inf'),
            5 
        )

        if max_potions > 0:
            bottler_plan.append({
                "potion_type": [potion_type.red_ml, potion_type.green_ml, potion_type.blue_ml, potion_type.dark_ml],
                "quantity": int(max_potions)
            })

            red_ml_left -= potion_type.red_ml * max_potions
            green_ml_left -= potion_type.green_ml * max_potions
            blue_ml_left -= potion_type.blue_ml * max_potions
            dark_ml_left -= potion_type.dark_ml * max_potions
    
    return bottler_plan

    

if __name__ == "__main__":
    print(get_bottle_plan())
