from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.FAIR_indicators_eval import computeScores_from_list
from app.helpers.utils import prepareMetadataForEvaluation
from app.helpers.database import connect_DB

router = APIRouter()

tools_collection, stats = connect_DB()

@router.post('/evaluate',  tags=["fair"])
async def evaluate(request: Request):
    data = await request.json()
    if data:
        tool = prepareMetadataForEvaluation(data['fair'])
        scores = computeScores_from_list([tool])
        return JSONResponse(content=scores)
    else:
        raise HTTPException(status_code=400, detail="No metadata provided")

@router.post('/evaluateId', tags=["fair"])
async def evaluateId(request: Request):
    data = await request.json()
    id_ = data.get('id')
    if id_:
        tool = tools_collection.find_one({'@id': id_})
        if tool:
            scores = computeScores_from_list([tool])
            return JSONResponse(content=scores)
        else:
            raise HTTPException(status_code=400, detail="No tool id or metadata provided")
    else:
        raise HTTPException(status_code=400, detail="No tool id or metadata provided")
