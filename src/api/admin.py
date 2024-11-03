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
        connection.execute(sqlalchemy.text("UPDATE capacity SET potion_capacity = 1, ml_capacity = 1"))

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100, red_ml = 0, green_ml = 0, blue_ml = 0, dark_ml = 0"))

        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {1}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {2}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {3}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {4}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {5}"))
        connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = 0 WHERE id = {6}"))

        connection.execute(sqlalchemy.text("DELETE FROM ml_ledger;"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (1,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (2,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (3,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (4,0);"))

        connection.execute(sqlalchemy.text("DELETE FROM gold_ledger;"))
        connection.execute(sqlalchemy.text(f"INSERT INTO gold_ledger (num_gold) VALUES (100);"))


        connection.execute(sqlalchemy.text("DELETE FROM potions_ledger;"))
        for id in range(1,6):
            connection.execute(sqlalchemy.text(f"INSERT INTO potions_ledger (pot_id, num_potions) VALUES ({id},0);"))

        
    return "OK"


