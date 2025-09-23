from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.utils import prepareToolMetadata, prepareMetadataForEvaluation, prepareListsIds, keep_first_label
from app.helpers.makejson import build_json_ld
from app.helpers.makecff import create_cff
from app.helpers.database import connect_DB
from bson import ObjectId

router = APIRouter()

tools_collection, stats, pubs_collection = connect_DB()



@router.get('/names_type_labels', tags=["tools"])
async def names_type_labels():
    tools = list(tools_collection.find({'source': {'$ne': ['galaxy_metadata']}}, {
        '_id': 0,
        'data.label': 1,
        'data.type': 1,
        'data.name': 1
    }))
    resp = [keep_first_label(tool) for tool in tools]
    return JSONResponse(content=resp)

@router.get('', tags=["tools"])
async def tool_metadata(name: str = None):
    if not name:
        raise HTTPException(status_code=400, detail="No tool name provided")
    tool = tools_collection.find_one({'data.name': name})
    if tool:
        pub_ids_raw = tool['data'].get("publication", [])
        if pub_ids_raw:
            def to_object_id(x):
                if isinstance(x, ObjectId):
                    return x
                if isinstance(x, str) and ObjectId.is_valid(x):
                    return ObjectId(x)
                return x  # leave as-is; you can also choose to drop/raise
            pub_ids = [to_object_id(x) for x in pub_ids_raw]

            # 2) Use the proper handle for the publications collection
            pubs = list(
                pubs_collection.find(
                    {"_id": {"$in": pub_ids}},
                    {"data": 1}  # _id is included by default unless excluded
                    )
            )
            print(pubs)
            # build order index from the pub_ids array
            idx = {pid: i for i, pid in enumerate(pub_ids)}
            # reorder pubs according to that index
            pubs.sort(key=lambda p: idx.get(p["_id"], 10**9))

            # replace with just the 'data' dicts
            tool['data']["publication"] = [p["data"] for p in pubs]

    tool = tool['data']
    if tool:
        #tool = prepareToolMetadata(tool)
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
