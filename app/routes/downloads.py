from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class URLRequest(BaseModel):
    url: str

@router.post("/download-content/", tags=["downloads"])
async def download_content(request: URLRequest):
    """
    Download content from a specified URL.

    This endpoint accepts a URL in the request body and returns the HTML content
    of the specified URL. If the URL is invalid or the content cannot be downloaded,
    it returns a 400 status code with an error message.

    Args:
        request (URLRequest): A JSON object containing the URL to be downloaded.

    Returns:
        dict: A dictionary containing the original URL and the downloaded content.
    """
    try:
        print(request.url)
        response = requests.get(request.url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading content: {e}")
    
    return {"url": request.url, "content": response.text}
