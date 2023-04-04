# FastAPI
from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException, status

# Pillow
from PIL import Image

# PyTesseract
import pytesseract

router = APIRouter(
    deprecated = True, ### DEPRECATED
    prefix = "/image",
    responses = {status.HTTP_409_CONFLICT: {"error": "Raw image"}}
)

### PATH OPERATIONS ###

## read image ##
@router.post(
    path="/",
    status_code = status.HTTP_200_OK,
    summary = "Read image",
    tags = ["Image"]
)
async def read_image(image :UploadFile = File(...)):
    return {
        "filename": image.filename,
        "content-type": image.content_type
    }

## image -> text ##
@router.post(
    path="/read/",
    status_code = status.HTTP_200_OK,
    summary = "Convert image to text",
    tags = ["Image"]
)
async def convert_image(
    image :UploadFile = File(...)
):
    # img = Image.open("")
    text = pytesseract.image_to_string(image)

    return text