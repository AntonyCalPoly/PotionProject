import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = 100, SET num_green_potions = 0, SET num_green_ml = 0"))
        connection.execute(sqlalchemy.text("DELETE FROM carts_log"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_items"))
    
    return "OK"

