import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        gold_in_inventory = connection.execute(sqlalchemy.text("SELECT SUM(num_gold) AS total_gold_amount FROM gold_ledger;")).fetchone()
        amount_potions = connection.execute(sqlalchemy.text("SELECT SUM(num_potions) AS total_potion_amount FROM potions_ledger;")).fetchone()
        ml_amount = connection.execute(sqlalchemy.text("SELECT SUM(red_ml + green_ml + blue_ml + dark_ml) AS total_ml_amount from global_inventory")).fetchone()
       # change ml_amount to take from ml_ledger instead of global_inventory
    return {"number_of_potions": amount_potions.total_potion_amount, "ml_in_barrels": ml_amount.total_ml_amount, "gold":gold_in_inventory.total_gold_amount}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    inventory = get_inventory()
    print(inventory)
    potion_cap = 1
    ml_cap = 1

    with db.engine.begin() as connection:
        info = connection.execute(sqlalchemy.text("SELECT potion_capacity, ml_capacity FROM capacity;")).fetchone()


    while potion_cap < 5:
        if(inventory["number_of_potions"] > (0.75 * info.potion_capacity * 50) and inventory["gold" > 1500]):
            potion_cap += 1

    while ml_cap < 5 and potion_cap > 2:
        if(inventory["number_of_potions"] > (0.75 * info.ml_capacity * 10000) and inventory["gold" > 1500]):
            ml_cap += 1

    return {
        "potion_capacity": potion_cap,
        "ml_capacity": ml_cap
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    # while potion_capacity < 5 and gold > 1500 buy potion_capacity
    # while ml_capacity < 5 and potion_capacity > 2 and gold > 1500 buy ml_capacity

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            '''UPDATE capacity SET
            potion_capacity = :potion_cap, 
            ml_capacity  = :ml_cap
            '''),
            {
                "potion_cap": capacity_purchase.potion_capacity,
                "ml_cap": capacity_purchase.ml_capacity
            }
            )


    return "OK"
