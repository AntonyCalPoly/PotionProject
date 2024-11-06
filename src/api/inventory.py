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
        ml_amount = connection.execute(sqlalchemy.text("SELECT SUM(num_ml) AS total_ml_amount from ml_ledger")).fetchone()
      
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

    with db.engine.begin() as connection:
        info = connection.execute(sqlalchemy.text("SELECT SUM(potion_capacity) AS potion_capacity, SUM(ml_capacity) AS ml_capacity FROM capacity;")).fetchone()
        potion_capacity, ml_capacity = info

    while potion_capacity < 5 and ml_capacity >= 2:
        if(inventory["gold"] > 1500):
            return {
                "potion_capacity": 1
            }

    while ml_capacity < 5:
        if(inventory["gold"] > 1500):
            return {
                "ml_capacity": 1
            }

    return {}

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
            '''INSERT INTO capacity
            (potion_capacity, ml_capacity)
            VALUES (:potion_cap, :ml_cap);

            INSERT INTO gold_ledger (num_gold)
            VALUES ((:potion_cap + :ml_cap) * -1000);
            
            UPDATE global_inventory SET gold = gold - (:potion_cap + :ml_cap) * 1000
            '''),
            {
                "potion_cap": capacity_purchase.potion_capacity,
                "ml_cap": capacity_purchase.ml_capacity
            }
            )


    return "OK"
