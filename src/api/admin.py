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
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100, red_ml = 0, green_ml = 0, blue_ml = 0, dark_ml = 0"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {1}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {2}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {3}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {4}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {5}"))
        
    return "OK"


