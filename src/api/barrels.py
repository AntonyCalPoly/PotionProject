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

    green_barrels_received = 0
    red_barrels_received = 0
    blue_barrels_received = 0
    tot_gold = 0

    for barrel in barrels_delivered:
        if barrel.sku == "SMALL_GREEN_BARREL":
            green_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity
        if barrel.sku == "SMALL_RED_BARREL":
            red_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity
        if barrel.sku == "SMALL_BLUE_BARREL":
            blue_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity


    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + ({green_barrels_received} WHERE sku = 'GREEN_POTION_0')"))

            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + ({red_barrels_received} WHERE sku = 'RED_POTION_0')"))

            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + ({blue_barrels_received} WHERE sku = 'BLUE_POTION_0')"))
            
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - ({tot_gold})"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT num_potions, sku, gold FROM global_inventory")).fetchall()

    potion_counts = {
        "GREEN_POTION_0": 0,
        "RED_POTION_0": 0,
        "BLUE_POTION_0": 0
    }

    gold = inventory[0].gold


    for entry in inventory:
        if entry.sku in potion_counts:
            potion_counts[entry.sku] = entry.num_potions

    barrels_needed = {
        "SMALL_GREEN_BARREL": 0,
        "SMALL_RED_BARREL": 0,
        "SMALL_BLUE_BARREL": 0
    }

    for barrel in wholesale_catalog:
        if barrel.price <= gold:
            if barrel.sku == "SMALL_GREEN_BARREL" and potion_counts["GREEN_POTION_0"] <= 10:
                barrels_needed["SMALL_GREEN_BARREL"] += 1
                gold -= barrel.price
            elif barrel.sku == "SMALL_RED_BARREL" and potion_counts["RED_POTION_0"] <= 10:
                barrels_needed["SMALL_RED_BARREL"] += 1
                gold -= barrel.price
            elif barrel.sku == "SMALL_BLUE_BARREL" and potion_counts["BLUE_POTION_0"] <= 10:
                barrels_needed["SMALL_BLUE_BARREL"] += 1
                gold -= barrel.price

    purchase_plan = [
        {"sku": sku, "quantity": quantity}
        for sku, quantity in barrels_needed.items() if quantity > 0
    ]
    
    return purchase_plan