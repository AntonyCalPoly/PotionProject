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
            num_mls = connection.execute(sqlalchemy.text("SELECT num_ml FROM global_inventory")).scalar()
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = ({num_mls + barrel.ml_per_barrel * barrel.quantity})"))
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - ({barrel.price * barrel.quantity})"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    purchase_plan = []

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT num_potions, sku, gold FROM global_inventory")).fetchall()

    green_pots = 0
    red_pots = 0
    blue_pots = 0
    gold = inventory[0].gold



    for entry in inventory:
        if entry.sku == "GREEN_POTION_0":
            green_pots = entry.num_potions
        if entry.sku == "RED_POTION_0":
            red_pots = entry.num_potions
        if entry.sku == "BLUE_POTION_0":
            blue_pots = entry.num_potions

    small_green_barrels_needed = 0
    small_red_barrels_needed = 0
    small_blue_barrels_needed = 0

    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_GREEN_BARREL" and green_pots <= 10 and barrel.price <= gold:
            small_green_barrels_needed +=1
            gold -= barrel.price

        if barrel.sku == "SMALL_RED_BARREL" and red_pots <= 10 and barrel.price <= gold:
            small_red_barrels_needed +=1
            gold -= barrel.price

        if barrel.sku == "SMALL_BLUE_BARREL" and blue_pots <= 10 and barrel.price <= gold:
            small_blue_barrels_needed +=1
            gold -= barrel.price
    
    if (small_green_barrels_needed > 0):
        purchase_plan.append({
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": small_green_barrels_needed,
            }
        })
    
    if (small_red_barrels_needed > 0):
        purchase_plan.append({
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": small_red_barrels_needed,
            }
        })
    
    if (small_blue_barrels_needed > 0):
        purchase_plan.append({
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": small_blue_barrels_needed,
            }
        })

    return purchase_plan