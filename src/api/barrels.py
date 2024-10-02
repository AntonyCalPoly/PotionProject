import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
            updateBarrels = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = ({num_green_ml + barrel.ml_per_barrel * barrel.quantity})"))
            updateGold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - ({barrel.price * barrel.quantity})"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        num_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()
        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
        green_pots = num_potions.num_green_potions
        gold = num_gold.gold
        quantity = 0
        if (green_pots < 10):   
        
            for barrel in wholesale_catalog:
                if barrel.sku == "SMALL_GREEN_BARREL" and barrel.price <= gold:
                    quantity +=1
        if quantity > 0:
            return [
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": quantity,
                }
            ]
        return []