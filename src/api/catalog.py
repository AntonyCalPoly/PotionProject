import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog = []

    with db.engine.begin() as connection:
         get_potions = connection.execute(sqlalchemy.text("SELECT id, num_potions, price, percent_red, percent_green, percent_blue, percent_dark, sku FROM custom_potions ORDER BY id DESC;")).fetchall()
       
    count_of_skus = 0

    for potion in get_potions:
        print(potion)
        if count_of_skus == 6:
            break
        if potion.num_potions > 0:
            count_of_skus += 1
            catalog.append({
                "sku": potion.id,
                "name": potion.sku,
                "quantity": potion.num_potions,
                "price": potion.price,
                "potion_type": [potion.percent_red, potion.percent_green, potion.percent_blue, potion.percent_dark],
            })
    
    return catalog