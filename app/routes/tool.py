from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB

router = APIRouter()

tools_collection, stats = connect_DB()


@router.get('/description')
async def description(name: str):
    try:
        entry = tools_collection.find_one({'name': name})
        data = {
            'name': name,
            'type': entry['type'],
            'description': entry['description'][0]
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Something went wrong while fetching tool description: {err}")
    return JSONResponse(content=data)


@router.post('/badge')
async def badge():
    badge = {
        "schemaVersion": 1,
        "label": "tool metadata",
        "message": "present",
        "color": "green",
        "logoSvg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"275.9\" height=\"314.9\" viewBox=\"0 0 73 83.3\"><path d=\"M99.1 65.3 90.4 60C90.2 60 80 78.3 80 78.4c0 .2 9.4 4.8 9.8 4.8 2.7-8.9 4.2-12 9.2-17.9zM89.5 56.8l-9.1-5.7c0 .1-13.3 22.5-13.2 22.6l9.8 5z\" style=\"fill:#fff;fill-opacity:1;stroke-width:.187202\" transform=\"translate(-67 -30.4)\"/><path d=\"M72.1 61c2.3-4 4.2-7 4.1-7.1v-.1c-5 1.5-8 7.3-8.5 11.1-.2 1.5 0 3.7.3 3.7L72 61z\" style=\"fill:#fff;fill-opacity:1;stroke:none;stroke-width:0;stroke-dasharray:none\" transform=\"translate(-67 -30.4)\"/><g style=\"fill:#fff\"><path d=\"M91.2 132.3a20.2 20.2 0 0 1-15-16.5c-.5-2.8-.5-3.4 0-6.2a20 20 0 0 1 18.6-16.8c5-.3 8.5.7 12.6 3.3l2 1.3 5.2-2.6c3-1.4 5.4-2.7 5.5-2.9 0 0-.2-1.5-.7-3.2-1.9-7-2-16.2-.4-23.4l1-3.7c2.5-7.5 2.3-7.4 7-14.1l1.7-2c6.5-8.4 17-15 27.7-17.7l3.2-.8v-7l.2-7-1.9-.7a23.3 23.3 0 1 1 17.5.1l-1.9.8v6.5l-.2 6.5 1.3.2a50.2 50.2 0 0 1 41 71.6 51.4 51.4 0 0 1-55 27.6 53.3 53.3 0 0 1-35.5-23c-.1 0-2.4 1-5 2.4-4.2 2.1-4.6 2.4-4.4 3l.4 3.6c.4 5.8-1.6 11-5.8 15.3a18.4 18.4 0 0 1-9.2 5.3c-3 .8-7 .8-9.9.1zm9.6-9.2a11.4 11.4 0 0 0 3.2-18.4 11.5 11.5 0 0 0-18.5 3.5 14 14 0 0 0 0 9.1c1.5 3.1 4.7 5.7 8 6.6 2 .5 5.3.1 7.3-.8zm72.9-19.2 1.6-4.1c.8-2 .8-2.1 2.6-2.8l1.9-.7 3.7 1.5 4.2 1.5c.2 0 1.4-1 2.8-2.2 2.8-2.5 2.8-2 6-6.9l-1.5-3.6.7-1.9c.6-1.4 1-1.7 2.3-2.2a86 86 0 0 0 4.1-1.7l2.6-1.2v-6.8l-4.1-1.6c-2.2-.9-4.2-1.7-4.3-2l-.8-1.7-.5-1.4 1.5-3.8c.9-2.1 1.5-4 1.5-4.3 0-.2-1.2-1.4-2.5-2.6l-2.4-2.3-1.8.7-4 1.7-2.3 1-1.8-.7c-1.3-.6-1.8-1-2.1-1.8l-1.8-4-1.3-2.8h-7.1l-1.2 2.7a93 93 0 0 0-1.6 4c-.3 1-.7 1.3-2.2 1.9l-1.8.7L155 55l-4.2-1.5c-.5 0-5.2 4.3-5.2 4.7l1.6 4.2 1.7 3.8-.7 1.7-.7 1.7-4 1.7-4 1.6-.2 3.5V80l2.3 1 4.2 1.6c1.6.5 1.8.7 2.4 2.3l.8 1.8-1.6 3.7-1.5 4.2c0 .4 1 1.6 2.3 2.9 2.7 2.5 2 2.5 7.2.3l3.4-1.5 1.8.7 1.8.7 1.4 3.5c2.2 5 1.8 4.8 5.7 4.8h3.3zM166 85a9 9 0 0 1-5.2-4.4c-.9-1.6-1-2.1-1-4.3 0-2.2.1-2.7 1-4.3a9.5 9.5 0 0 1 16.6 0c.8 1.5 1 2.2 1 4.3 0 2.2-.1 2.7-1 4.3a9.4 9.4 0 0 1-5.5 4.5c-2.3.6-3.7.6-5.9-.1zm4.1-81.6c8.3-2.2 12.3-12 8-19.4a13.1 13.1 0 1 0-8 19.3z\" style=\"fill:#fff;fill-opacity:1;stroke-width:.33218\" transform=\"matrix(.50368 0 0 .50368 -38.2 16.4)\"/></g></svg>"
    }
    return JSONResponse(content=badge)

@router.post('/badge/test')
async def badge_test():
    badge = {
        "schemaVersion": 1,
        "label": "tool metadata",
        "message": "present",
        "color": "green",
    }
    return JSONResponse(content=badge)