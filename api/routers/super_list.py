# Typing
# from typing import 
from pydantic import HttpUrl

# FastAPI
from fastapi import APIRouter, Path, Body, Query, File, UploadFile, Depends
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

# Requests
import requests

# Beautifulsoap4
from bs4 import BeautifulSoup

# auth
from auth import get_current_user

# db
from db.deta_db import db_super
from db.deta_db import drive_super_lists

# models
from db.models.user import User
from db.models.supermarket_list import SuperList, Products


router = APIRouter(
    prefix = "/super"
)

## PATH OPERATIONS ##

### Show supermarket lists ###
@router.get(
    path = "/{username}",
    status_code = status.HTTP_200_OK,
    # response_model = list[SuperList] | SuperList | dict,
    summary = "Show all supermarket lists for a user",
    tags = ["Supermarket list"]
)
async def supermarket_lists(
    current_user: User = Depends(get_current_user)
):
    try:
        super_lists = db_super.fetch({"username": current_user.username})
    except:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = {
                "errmsg": "DB error"
            }
        )
    
    return super_lists

### Show a supermarket list ###
@router.get(
    path = "/{order}",
    status_code = status.HTTP_200_OK,
    response_model = SuperList,
    summary = "Show a supermarket list with the order ID",
    tags = ["Supermarket list"]
)
async def supermarket_list(
    current_user: User = Depends(get_current_user),
    order: str = Path(...)
):
    try:
        super_list = db_super.fetch(
            {"username": current_user.username},
            {"order": order}
        )
    except:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "DB error"
            }
        )
    
    if not super_list:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {
                "errmsg": "Order not found"
            }
        )
    
    return super_list

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
    order_id: str = Query(),
    products: Products = Body(...)
):
    try:
        insert = SuperList(
            username = current_user.username,
            order = order_id,
            products = products.dict()
        )
        db_super.put(
            data = jsonable_encoder(insert),
            key = order_id
        )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "List not inserted",
                "errdetail": str(err)
            }
        )
    
    return SuperList(**db_super.get(order_id))

### Register a CSV ###
@router.post(
    path = "/url",
    status_code = status.HTTP_201_CREATED,
    response_model = SuperList,
    summary = "Register a supermarket list with the url",
    tags = ["Supermarket list"]
)
async def register_supermarket_list_with_url(
    current_user: User = Depends(get_current_user),
    details: dict = Body(
        ...,
        example = {
            "url": "https:miurl.com",
            "order": "423423",
            "date": "2023-12-30"
            }
    )
):
    try:
        page = requests.get(details.url)
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
        
        db_super.put(
            data = SuperList(
                username = current_user.username,
                order = details.order,
                date = details.date,
                products = data
            ),
            key = details.order
        )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "ERROR",
                "errdetail": str(err)
            }
        )
    
    inserted_data = db_super.get(details.order)
    if not inserted_data:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "Data not inserted"
            }
        )
    
    return SuperList(**inserted_data)

### Register a supermarket list with img ###
router.post(
    path = "/img",
    status_code = status.HTTP_202_ACCEPTED,
    response_model = SuperList,
    summary = "Register a supermarket list with a img",
    tags = ["Supermarket list"],
    deprecated = True
)
async def register_supermarket_list_img(
    current_user: User = Depends(get_current_user),
    order_id: str = Body(),
    img: UploadFile = File()
):
    try:
        drive_super_lists.put(
            name = f'{current_user.username}&&{order_id}',
            data = img.file,
            content_type = img.content_type
        )
    except Exception as err:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = {
                "errmsg": "Drive error",
                "errdetail": str(err)
            }
        )
    
    return f'{current_user.username}&&{order_id}'