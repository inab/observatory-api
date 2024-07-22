from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.utils import prepareToolMetadata, prepareMetadataForEvaluation, prepareListsIds, keep_first_label
from app.helpers.makejson import build_json_ld
from app.helpers.makecff import create_cff
from app.helpers.database import connect_DB

router = APIRouter()

tools_collection, stats = connect_DB()



@router.get('/names_type_labels', tags=["tools"])
async def names_type_labels():
    tools = list(tools_collection.find({'source': {'$ne': ['galaxy_metadata']}}, {
        '_id': 0,
        '@id': 1,
        'label': 1,
        'type': 1,
        'sources_labels': 1,
        'name': 1
    }))
    resp = [keep_first_label(tool) for tool in tools]
    return JSONResponse(content=resp)

@router.get('/', tags=["tools"])
async def tool_metadata(name: str = None, type_: str = None):
    if not name and not type_:
        raise HTTPException(status_code=400, detail="No tool name or type provided")
    tool = tools_collection.find_one({'name': name, 'type': type_})
    if tool:
        tool = prepareToolMetadata(tool)
        tool = prepareListsIds(tool)
        return JSONResponse(content=tool)
    else:
        raise HTTPException(status_code=400, detail="Something went wrong :(")


@router.get('/all', tags=["tools"])
async def get_all_tools():
    try:
        tools = list(tools_collection.find({}))
        for entry in tools:
            entry.pop('_id', None)
        data = {'tools': tools}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Something went wrong while fetching tool entries: {err}")
    return JSONResponse(content={'message': data, 'code': 'SUCCESS'})


@router.post('/jsonld', tags=["tools"])
async def tool_jsonld(request: Request):
    tool = await request.json()
    tool = tool['data']
    try:
        tool = prepareMetadataForEvaluation(tool)
        tool = build_json_ld(tool)
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when building the JSON-LD :(")
    return JSONResponse(content=tool)

@router.post('/cff', tags=["tools"])
async def tool_cff(request: Request):
    tool = await request.json()
    tool = tool['data']
    try:
        tool = prepareMetadataForEvaluation(tool)
        cff = create_cff(tool)
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when building the CFF :(")
    return JSONResponse(content=cff)
