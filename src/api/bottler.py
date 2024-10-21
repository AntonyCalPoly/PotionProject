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
           
            custom_potion = connection.execute(sqlalchemy.text("SELECT id FROM custom_potions where percent_red = :red_ml AND percent_green = :green_ml AND percent_blue = :blue_ml AND percent_dark = :dark_ml;"),
                {
                "red_ml": potion.potion_type[0] * 100,
                "green_ml": potion.potion_type[1] * 100,
                "blue_ml": potion.potion_type[2] * 100,
                "dark_ml": potion.potion_type[3] * 100
            }).fetchone()       
           
            if custom_potion:
                connection.execute(sqlalchemy.text("UPDATE custom_potions SET num_potions = num_potions + :quantity WHERE id = :id;"),
                    {"quantity": potion.quantity, "id": custom_potion.id})  
                
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = red_ml - :red_ml, green_ml = green_ml - :green_ml, blue_ml = blue_ml - :blue_ml, dark_ml = dark_ml - :dark_ml;"),
                    {
                    "red_ml": potion.potion_type[0] * potion.quantity * 100,
                    "green_ml": potion.potion_type[1] * potion.quantity * 100,
                    "blue_ml": potion.potion_type[2] * potion.quantity * 100,
                    "dark_ml": potion.potion_type[3] * potion.quantity * 100
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

        get_potions = connection.execute(sqlalchemy.text("SELECT percent_red, percent_green, percent_blue, percent_dark, id FROM custom_potions;")).fetchall()

    bottler_plan = []

    red_ml_left, green_ml_left, blue_ml_left, dark_ml_left = get_inventory

    for potion_type in get_potions:
        percent_red = potion_type[0]
        percent_green = potion_type[1]
        percent_blue = potion_type[2]
        percent_dark = potion_type[3]

        max_potions = min(
            red_ml_left // percent_red if percent_red > 0 else float('inf'),
            green_ml_left // percent_green if percent_green > 0 else float('inf'),
            blue_ml_left // percent_blue if percent_blue > 0 else float('inf'),
            dark_ml_left // percent_dark if percent_dark > 0 else float('inf'),
            5  
        )

        if max_potions > 0:
            bottler_plan.append({
                "potion_type": [percent_red, percent_green, percent_blue, percent_dark],
                "quantity": int(max_potions)
            })

            red_ml_left -= percent_red * max_potions
            green_ml_left -= percent_green * max_potions
            blue_ml_left -= percent_blue * max_potions
            dark_ml_left -= percent_dark * max_potions

    return bottler_plan

    
if __name__ == "__main__":
    print(get_bottle_plan())