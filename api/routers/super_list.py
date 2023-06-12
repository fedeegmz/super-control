# Python
from datetime import date, timedelta

# FastAPI
from fastapi import APIRouter, Path, Body, Query, Depends
from fastapi import status
from fastapi.encoders import jsonable_encoder

# Requests
import requests

# Beautifulsoap4
from bs4 import BeautifulSoup

# exceptions
from exceptions import HTTPError

# db
from db.mongo_client import db_client

# auth
from auth import get_current_user

# models
from db.models.user import User
from db.models.supermarket_list import BaseSuperList, SuperList, Products


router = APIRouter(
    prefix = "/super"
)

## PATH OPERATIONS ##

### Show supermarket lists ###
@router.get(
    path = "/",
    status_code = status.HTTP_200_OK,
    # response_model = list[SuperList] | SuperList | dict,
    summary = "Show all supermarket lists for a user",
    tags = ["Supermarket list"]
)
async def supermarket_lists(
    current_user: User = Depends(get_current_user)
):
    super_lists = db_client.get_available_superlist_for_user(current_user.username)

    if len(super_lists) != 0:
        super_lists_to_return = [SuperList(**super_list).dict() for super_list in super_lists]
    else:
        super_lists_to_return = []
    
    return super_lists_to_return

### Show a supermarket list ###
@router.get(
    path = "/{order_id}",
    status_code = status.HTTP_200_OK,
    response_model = SuperList,
    summary = "Show a supermarket list with the order ID",
    tags = ["Supermarket list"]
)
async def supermarket_list(
    current_user: User = Depends(get_current_user),
    order_id: str = Path(...)
):
    super_list = db_client.get_superlist_with_orderid(
        username = current_user.username,
        order_id = order_id
    )
    
    if not super_list:
        raise HTTPError().not_found(message="Order not found")
    
    return super_list.dict()

### Register a supermarket list ###
@router.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = SuperList,
    summary = "Register a supermarket list",
    tags = ["Supermarket list"]
)
async def register_supermarket_list(
    current_user: User = Depends(get_current_user),
    order: str = Query(...),
    issue_date: str = Query(),
    products: list[Products] = Body(...)
):
    insert = SuperList(
            username = current_user.username,
            order = order,
            issue_date = issue_date,
            products = jsonable_encoder(
                [product.description.strip().lower() for product in products]
            )
        )
    
    inserted_data = db_client.insert_superlist(insert.dict())
    if not inserted_data:
        raise HTTPError().not_found(message="List not inserted")
    
    return inserted_data.dict()

### Register a supermarket list with a url ###
@router.post(
    path = "/url",
    status_code = status.HTTP_201_CREATED,
    response_model = SuperList,
    summary = "Register a supermarket list with the url",
    tags = ["Supermarket list"]
)
async def register_supermarket_list_with_url(
    current_user: User = Depends(get_current_user),
    details: BaseSuperList = Body(...)
):
    details_dict = details.dict()
    url = details_dict.get("url")
    order_id = details_dict.get("order")
    issue_date = details_dict.get("issue_date")
    supermarket = details_dict.get("supermarket")

    if not url or not order_id or not issue_date:
        raise HTTPError().bad_request(message="url/order/issue_date not recived")
    
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        rows = soup.find_all("tr", class_="font table-full-alt")

        data = []
        for row in rows:
            description = row.find("div").text
            units_and_price = row.find_all("div", class_="center")
            units = units_and_price[0].text
            price = units_and_price[1].text
            
            data.append(
                Products(
                    description = str(description).strip().lower(),
                    units = float(units),
                    price = float(price)
                ))
        
        insert = SuperList(
                    username = current_user.username,
                    order = order_id,
                    issue_date = issue_date,
                    supermarket = supermarket,
                    products = data
                )
    except Exception as err:
        raise HTTPError().conflict(message="ERROR", err=str(err))
    
    inserted_data = db_client.insert_superlist(insert)
    if not inserted_data:
        raise HTTPError().not_found(message="Data not inserted")
    
    return inserted_data.dict()

### Update a supermarket list ###
@router.post(
    path = "/{order_id}",
    status_code = status.HTTP_200_OK,
    response_model = SuperList,
    summary = "Update a supermarket list with the orderID",
    tags = ["Supermarket list"]
)
async def update_supermarket_list(
    current_user: User = Depends(get_current_user),
    order_id: str = Path(...),
    updates: list[dict] = Body(
        ...,
        example = [
            {"order": "12345"},
            {"issue_date": "2023-12-30"}
        ]
    )
):
    # strip() and lower() to product.description
    if updates.get("description", None):
        updates["description"] = updates["description"].strip().lower()
    
    super_list_updated = db_client.get_superlist_with_orderid_and_update(
        username = current_user.username,
        order_id = order_id,
        updates = updates
    )

    if not super_list_updated:
        raise HTTPError().conflict(message="Supermarket list not updated")
    
    return super_list_updated.dict()

### Delete a supermarket list ###
@router.delete(
    path = "/{order_id}",
    status_code = status.HTTP_200_OK,
    response_model = SuperList,
    summary = "Delete a supermarket list with the orderID",
    tags = ["Supermarket list"]
)
async def delete_supermarket_list(
    current_user: User = Depends(get_current_user),
    order_id: str = Path(...)
):
    super_list_deleted = db_client.get_superlist_with_orderid_and_update(
        username = current_user.username,
        order_id = order_id,
        updates = [{"disabled": True}]
    )

    if not super_list_deleted:
        raise HTTPError().conflict(message="Supermarket list not deleted")
    
    return super_list_deleted.dict()

## Interesting Cards ##

### amount per period ###
@router.get(
    path = "/amount-per-period/{product_description}",
    status_code = status.HTTP_200_OK,
    response_model = int,
    summary = "Get the quantity of a product in a period",
    tags = ["Supermarket list", "Icard"]
)
async def amount_per_period(
    current_user: User = Depends(get_current_user),
    product_description: str = Path(...),
    start: date = Query(default=date.today() - timedelta(days=30)),
    end: date = Query(default=date.today())
):
    product_description = product_description.strip().lower()
    result = db_client.superlist_mongo_db.find(
        {
            "username": current_user.username,
            "products.description": product_description,
            "issue_date": {"$lte": str(end)},
            "issue_date": {"$gte": str(start)}
        },
        {
            "_id": 0,
            "description": "$products.description",
            "price": 1
        }
    )

    return len(result)
    # results = db_client.superlist_mongo_db.aggregate([
    #     {"$match": 
    #         {
    #             "username": current_user.username,
    #             "products.description": product_description,
    #             "issue_date": {"$gte": start},
    #             "issue_date": {"$lte": end}
    #         }
    #     },
    #     {
    #         "$group":
    #             {
    #                 "_id": "$products.description",
    #                 "total": {"$sum": "$products.price"}
    #             }
    #     }
    # ])