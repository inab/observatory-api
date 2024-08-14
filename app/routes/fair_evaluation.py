from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from app.helpers.FAIR_indicators_eval import computeScores_from_list
from app.helpers.utils import prepareMetadataForEvaluation
from app.helpers.database import connect_DB
from app.models.instance import Instance
from app.services.indicator_computation import IndicatorComputation
from app.services.fair_scores import compute_fair_scores
from app.constants import WEB_TYPES
from app.models.fair_metrics import FAIRmetrics, FAIRscores  # Import the necessary classes



router = APIRouter()

tools_collection, stats = connect_DB()

''' OLD CODE
@router.post('/evaluate',  tags=["fair"])
async def evaluate(request: Request):
    data = await request.json()
    if data:
        tool = prepareMetadataForEvaluation(data['tool_metadata'])
        scores = computeScores_from_list([tool])
        return JSONResponse(content=scores)
    else:
        raise HTTPException(status_code=400, detail="No metadata provided")
'''

@router.post("/evaluate", tags=["fair"])
async def evaluate(request: Request, prepare: bool = Query(True, description="Indicate whether the metadata needs preparation")):
    data = await request.json()
    if data and 'tool_metadata' in data:
        tool_metadata = data['tool_metadata']

        # Check if preparation is needed
        if prepare:
            prepared_tool = prepareMetadataForEvaluation(tool_metadata)
        else:
            prepared_tool = tool_metadata
        # Create an instance object
        instance = Instance(**prepared_tool)
        
        # Set super type based on web types
        instance.set_super_type(WEB_TYPES)
        
        # Compute metrics
        computation = IndicatorComputation(instance)
        computation.compute_indicators()
        
        # Compute FAIR scores and get the result dictionary
        result = compute_fair_scores(instance)
        logs = instance.logs.__dict__

        data = {
            'result': result,
            'logs': logs
        }
        
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=400, detail="No metadata provided")

@router.post('/evaluateId', tags=["fair"])
async def evaluateId(request: Request):
    data = await request.json()
    id_ = data.get('id')
    if id_:
        tool = tools_collection.find_one({'@id': id_})
        if tool:
            # Create an instance object
            instance = Instance(**tool)
            
            # Set super type based on web types
            instance.set_super_type(WEB_TYPES)
            
            # Compute metrics
            computation = IndicatorComputation(instance)
            computation.compute_indicators()
            
            # Compute FAIR scores and get the result dictionary
            result = compute_fair_scores(instance)
            
            logs = instance.logs.__dict__

            data = {
                'result': result,
                'logs': logs
            }
            return JSONResponse(content=data)
        else:
            raise HTTPException(status_code=400, detail="No tool id or metadata provided")
    else:
        raise HTTPException(status_code=400, detail="No tool id or metadata provided")



