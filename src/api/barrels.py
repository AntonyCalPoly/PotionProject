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
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            sql = """
            UPDATE inventory
            SET red_ml = red_ml + :red_ml,
                green_ml = green_ml + :green_ml,
                blue_ml = blue_ml + :blue_ml,
                dark_ml = dark_ml + :dark_ml,
                gold = gold - :price
            """
            connection.execute(sqlalchemy.text(sql), {
                "red_ml": barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[0],
                "green_ml": barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[1],
                "blue_ml": barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[2],
                "dark_ml": barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[3],
                "price": barrel.price * barrel.quantity
            })
    return "OK"
    
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml, gold FROM global_inventory")).fetchone()
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
    print(purchase_plan)           
    return purchase_plan