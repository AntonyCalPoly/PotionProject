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
        gold_in_inventory = connection.execute(sqlalchemy.text("SELECT SUM(gold) AS total_gold_amount FROM global_inventory;")).fetchone()
        amount_potions = connection.execute(sqlalchemy.text("SELECT SUM(num_potions) AS total_potion_amount FROM custom_potions;")).fetchone()
        ml_amount = connection.execute(sqlalchemy.text("SELECT SUM(red_ml + green_ml + blue_ml + dark_ml) AS total_ml_amount from global_inventory")).fetchone()
       
    return {"number_of_potions": amount_potions.total_potion_amount, "ml_in_barrels": ml_amount.total_ml_amount, "gold":gold_in_inventory.total_gold_amount}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"
