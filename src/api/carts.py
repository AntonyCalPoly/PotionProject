import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"SELECT customer_name, character_class, level, cart_id, quantity, payment FROM cart WHERE customer_name = '{new_cart.customer_name}' and character_class = '{new_cart.character_class}' and level = '{new_cart.level}';"))
        result_new = result.fetchall()
        if len(result_new) == 0 :
            update_id  = connection.execute(sqlalchemy.text("SELECT cart_id FROM cart ORDER BY cart_id DESC")).fetchone()
            cart_id = (update_id[0]+1)
            connection.execute(sqlalchemy.text(f"INSERT INTO cart (customer_name, character_class, level, cart_id, quantity, payment) VALUES ('{new_cart.customer_name}','{new_cart.character_class}',{new_cart.level},{cart_id},{0},{0});"))
        else:
            cart_id = result_new[0][3]
            connection.execute(sqlalchemy.text(f"UPDATE cart SET quantity = 0, payment = 0 WHERE customer_name = '{new_cart.customer_name}' and character_class = '{new_cart.character_class}' and level = '{new_cart.level}';"))
    
    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        price_of_potions = connection.execute(sqlalchemy.text(f"SELECT cost FROM global_inventory WHERE sku = '{item_sku}';")).fetchone()
        connection.execute(sqlalchemy.text(f"UPDATE cart SET quantity = {cart_item.quantity}, payment = payment + {cart_item.quantity * price_of_potions.price} WHERE cart_id = {cart_id};"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_potions = num_potions - {cart_item.quantity} WHERE sku = '{item_sku}';"))

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text(f"SELECT quantity,payment FROM cart WHERE cart_id = {cart_id};"))
        inventory_checkout = inventory.fetchone()
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold + {inventory_checkout.payment}"))

    return {"total_potions_bought": {inventory_checkout.quantity}, "total_gold_paid": {inventory_checkout.payment}}
