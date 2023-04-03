# FastAPI
from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException, status

router = APIRouter(
    prefix = "/image",
    responses = {status.HTTP_409_CONFLICT: {"error": "Raw image"}}
)

### PATH OPERATIONS ###

## read image ##
@router.post(
    path="/read/",
    status_code = status.HTTP_200_OK,
    summary = "Read image",
    tags = ["Image"]
)
async def read_image(image :UploadFile = File(...)):
    return {
        "filename": image.filename,
        "content-type": image.content_type
    }