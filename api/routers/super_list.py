# FastAPI
from fastapi import APIRouter, Path, Body, Query, Depends
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# Requests
import requests

# Beautifulsoap4
from bs4 import BeautifulSoup

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
    super_list = db_client.get_superlist_with_orderid(order_id)
    
    if not super_list:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {
                "errmsg": "Order not found"
            }
        )
    
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
            products = jsonable_encoder(products)
        )
    
    inserted_data = db_client.insert_superlist(insert.dict())
    if not inserted_data:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {
                "errmsg": "List not inserted"
            }
        )
    
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

    if not url or not order_id or not issue_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "errmsg": "url/order/issue_date not recived"
            }
        )
    
    try:
        page = await requests.get(url)
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
                    description = description,
                    units = units,
                    price = price
                ))
        
        insert = SuperList(
                    username = current_user.username,
                    order = order_id,
                    issue_date = issue_date,
                    products = data
                )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "ERROR",
                "errdetail": str(err)
            }
        )
    
    inserted_data = db_client.insert_superlist(insert)
    if not inserted_data:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {
                "errmsg": "Data not inserted"
            }
        )
    
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
    order_id: str = Path(...),
    updates: dict = Body(
        ...,
        example = {
            "order": "12345",
            "issue_date": "2023-12-30"
        }
    )
):
    super_list_updated = db_client.get_superlist_with_orderid_and_update(
        order_id = order_id,
        updates = updates
    )

    if not super_list_updated:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "Supermarket list not updated"
            }
        )
    
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
    order_id: str = Path(...)
):
    super_list_deleted = db_client.get_superlist_with_orderid_and_update(
        order_id = order_id,
        updates = {"disabled": True}
    )

    if not super_list_deleted:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "Supermarket list not deleted"
            }
        )
    
    return super_list_deleted.dict()