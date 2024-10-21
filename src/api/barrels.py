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

    red_barrels_received = 0
    green_barrels_received = 0
    blue_barrels_received = 0
    dark_barrels_received = 0
    tot_gold = 0

    for barrel in barrels_delivered:
        if barrel.sku == "SMALL_RED_BARREL":
            red_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity
        if barrel.sku == "SMALL_GREEN_BARREL":
            green_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity
        if barrel.sku == "SMALL_BLUE_BARREL":
            blue_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity
        if barrel.sku == "SMALL_DARK_BARREL":
            dark_barrels_received += barrel.quantity * barrel.ml_per_barrel 
            tot_gold += barrel.price * barrel.quantity


    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET red_ml = red_ml + {red_barrels_received};"))

            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET green_ml = green_ml + {green_barrels_received};"))

            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET blue_ml = blue_ml + {blue_barrels_received};"))
            
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET dark_ml = dark_ml + {dark_barrels_received};"))

            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - ({tot_gold})"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml, gold FROM global_inventory")).fetchall()
        red_ml, green_ml, blue_ml, dark_ml, gold = inventory
        purchase_plan = []

        for barrel in wholesale_catalog:
            current_ml = (
            red_ml * barrel.potion_type[0] +
            green_ml * barrel.potion_type[1] +
            blue_ml * barrel.potion_type[2] +
            dark_ml * barrel.potion_type[3]
        )

        if current_ml < 500 and gold >= barrel.price:
            purchase_plan.append({
                "sku": barrel.sku,
                "quantity": 1
            })
            gold -= barrel.price
            red_ml += barrel.ml_per_barrel * barrel.potion_type[0]
            green_ml += barrel.ml_per_barrel * barrel.potion_type[1]
            blue_ml += barrel.ml_per_barrel * barrel.potion_type[2]
            dark_ml += barrel.ml_per_barrel * barrel.potion_type[3]
    
    return purchase_plan