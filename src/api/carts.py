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

    if sort_col is search_sort_options.customer_name:
        order_by = db.cart.c.customer_name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.custom_potions.c.id
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.cart.c.payment
    elif sort_col is search_sort_options.timestamp:
        order_by = db.cart.c.created_at
    else:
        assert False

    if search_page != "":
        current_offset = int(search_page) * 5
        previous_offset = current_offset - 5
    else:
        current_offset = 0

    next_offset = current_offset + 5

    current_page = (
        sqlalchemy.select(
            db.cart.c.customer_name,
            db.custom_potions.c.sku,
            db.cart.c.payment,
            db.cart.c.created_at
        ).join(
            db.cart_items, db.cart_items.c.cart_id == db.cart.c.cart_id
        ).join(
            db.custom_potions, db.custom_potions.c.id == db.cart_items.c.potion_type
        )
        .order_by(order_by, db.cart.c.created_at)
        .offset(current_offset) 
        .limit(5)
    )

    if current_offset > 0:
        previous_page = (
            sqlalchemy.select(
                db.cart.c.customer_name,
                db.custom_potions.c.sku,
                db.cart.c.payment,
                db.cart.c.created_at
            ).join(
                db.cart_items, db.cart_items.c.cart_id == db.cart.c.cart_id
            ).join(
                db.custom_potions, db.custom_potions.c.id == db.cart_items.c.potion_type
            )
            .order_by(order_by, db.cart.c.created_at)
            .offset(previous_offset) 
            .limit(5)
            )

    next_page = (
       sqlalchemy.select(
                db.cart.c.customer_name,
                db.custom_potions.c.sku,
                db.cart.c.payment,
                db.cart.c.created_at
            ).join(
                db.cart_items, db.cart_items.c.cart_id == db.cart.c.cart_id
            ).join(
                db.custom_potions, db.custom_potions.c.id == db.cart_items.c.potion_type
            )
            .order_by(order_by, db.cart.c.created_at)
            .offset(next_offset) 
            .limit(5)
    )

    if customer_name != "":
        current_page = current_page.where(db.cart.c.customer_name.like(f"%{customer_name}%"))

    if potion_sku != "":
        current_page = current_page.where(db.custom_potions.c.sku.like(f"%{potion_sku}%"))

    previous_json = ""

    with db.engine.connect() as conn:
        current_result = conn.execute(current_page)
        current_json = []
        for row in current_result:
            current_json.append(
                {
                    "customer_name": row.customer_name,
                    "item_sku": row.sku,
                    "line_item_total": row.payment,
                    "timestamp": row.created_at
                }
            )
        if current_offset > 0:
            previous_result = conn.execute(previous_page)
            previous_json = []
            for row in previous_result:
                previous_json.append(
                    {
                        "customer_name": row.customer_name,
                        "item_sku": row.sku,
                        "line_item_total": row.payment,
                        "timestamp": row.created_at
                    }
                )
        next_result = conn.execute(next_page)
        next_json = []
        for row in next_result:
            next_json.append(
                {
                    "customer_name": row.customer_name,
                    "item_sku": row.sku,
                    "line_item_total": row.payment,
                    "timestamp": row.created_at
                }
            )
    
    return {
        "previous": previous_json,
        "results": current_json,
        "next": next_json
    }

'''
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
'''

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
        result = connection.execute(sqlalchemy.text(f"INSERT INTO cart (customer_name, character_class, level, quantity, payment) VALUES ('{new_cart.customer_name}','{new_cart.character_class}',{new_cart.level},{0},{0}) RETURNING cart_id;")).fetchone()

    return {"cart_id": result.cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO cart_items (cart_id, potion_type, quantity) VALUES ({cart_id},{item_sku}, {cart_item.quantity});"))
       
        price_of_potions = connection.execute(sqlalchemy.text(f"SELECT price FROM custom_potions WHERE id = '{item_sku}';")).fetchone()
        
        connection.execute(sqlalchemy.text("UPDATE cart SET quantity = :quantity, payment = payment + :payment WHERE cart_id = :cart_id;"),
                   {"quantity": cart_item.quantity, "payment": cart_item.quantity * price_of_potions.price, "cart_id": cart_id})

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        potions_bought = connection.execute(sqlalchemy.text(f"SELECT potion_type, quantity FROM cart_items WHERE cart_id = {cart_id};")).fetchall()
       
        checkout = connection.execute(sqlalchemy.text(f"SELECT quantity AS quantity,payment FROM cart WHERE cart_id = {cart_id};")).fetchone()

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold + {checkout.payment} WHERE id = 1;"))

        for potion in potions_bought:
            connection.execute(sqlalchemy.text(f"UPDATE custom_potions SET num_potions = num_potions - {potion.quantity} WHERE id = {potion.potion_type};"))
       
        potion_ledger_update = connection.execute(sqlalchemy.text(
            '''INSERT INTO potions_ledger 
            (pot_id, num_potions) 
            VALUES ((SELECT potion_type FROM cart_items WHERE cart_id = :cart_id), 
            (SELECT -quantity FROM cart_items WHERE cart_id = :cart_id))
            RETURNING num_potions'''),
            {
                "cart_id": cart_id
            }
            ).fetchone()
        
        gold_ledger_update = connection.execute(sqlalchemy.text(
            '''INSERT INTO gold_ledger
            (num_gold) 
            VALUES ((SELECT payment FROM cart WHERE cart_id = :cart_id))
            RETURNING num_gold'''),
            {
                "cart_id": cart_id
            }
            ).fetchone()
            
    return {"total_potions_bought": -potion_ledger_update.num_potions, "total_gold_paid": gold_ledger_update.num_gold}