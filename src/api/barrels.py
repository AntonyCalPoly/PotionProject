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
    print(f"Barrels delivered: {barrels_delivered}, Order ID: {order_id}")
    
    with db.engine.begin() as connection:
        initial_inventory = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml, gold FROM global_inventory")).fetchone()
        print(f"Initial inventory: {initial_inventory}")

        for barrel in barrels_delivered:
            red_ml_update = barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[0]
            green_ml_update = barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[1]
            blue_ml_update = barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[2]
            dark_ml_update = barrel.ml_per_barrel * barrel.quantity * barrel.potion_type[3]
            price_update = barrel.price * barrel.quantity
            
            print(f"Updating with: red_ml: {red_ml_update}, green_ml: {green_ml_update}, blue_ml: {blue_ml_update}, dark_ml: {dark_ml_update}, price: {price_update}")

            sql = """
            UPDATE global_inventory
            SET red_ml = red_ml + :red_ml,
                green_ml = green_ml + :green_ml,
                blue_ml = blue_ml + :blue_ml,
                dark_ml = dark_ml + :dark_ml,
                gold = gold - :price
            """
            connection.execute(sqlalchemy.text(sql), {
                "red_ml": red_ml_update,
                "green_ml": green_ml_update,
                "blue_ml": blue_ml_update,
                "dark_ml": dark_ml_update,
                "price": price_update
            })
        
        updated_inventory = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml, gold FROM global_inventory")).fetchone()
        print(f"Updated inventory: {updated_inventory}")

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
            print(f"Bought barrel: {barrel.sku}, remaining gold: {gold}")
            red_ml += barrel.ml_per_barrel * barrel.potion_type[0]
            green_ml += barrel.ml_per_barrel * barrel.potion_type[1]
            blue_ml += barrel.ml_per_barrel * barrel.potion_type[2]
            dark_ml += barrel.ml_per_barrel * barrel.potion_type[3]
            print(f"Updated ML - red: {red_ml}, green: {green_ml}, blue: {blue_ml}, dark: {dark_ml}")
    print(purchase_plan)           
    return purchase_plan
