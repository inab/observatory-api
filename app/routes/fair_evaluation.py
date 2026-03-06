from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from app.helpers.FAIR_indicators_eval import computeScores_from_list
from app.helpers.indicators_feedback import get_feedback
from app.helpers.utils import prepareMetadataForEvaluation
from app.helpers.database import connect_DB
from app.models.instance import Instance
from app.services.indicator_computation import IndicatorComputation
from app.services.fair_scores import compute_fair_scores
from app.constants import WEB_TYPES
from app.models.fair_metrics import FAIRmetrics, FAIRscores  # Import the necessary classes
from typing import Dict, Any, Optional, Annotated
from pydantic import BaseModel, ConfigDict, Field
import logging
import traceback



router = APIRouter()

tools_collection, stats, pubs_collection, availability_collection = connect_DB()

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

class MetadataRequest(BaseModel):
    tool_metadata: Dict[str, Any] = Field(
        ...,
        description="The metadata related to the tool that needs to be evaluated."
    )
    prepare: Optional[bool] = Field(
        True,
        description="Indicates whether the metadata needs to be prepared before evaluation. Defaults to True."
    )


@router.post("/evaluate", tags=["fair"])
async def evaluate(
        request: Request,
        data: Annotated[
            MetadataRequest,
            Body(
                openapi_examples={
                    "minimal": {
                        "summary": "Minimal request",
                        "description": "Smallest useful payload to run FAIRsoft evaluation.",
                        "value": {
                            "tool_metadata": {
                                "name": "Flower",
                                "type": "lib",
                                "repository": [
                                    "https://github.com/adap/flower"
                                ],
                                "version_control": True
                            },
                            "prepare": False
                        },
                    },
                    "richer": {
                        "summary": "Richer request",
                        "description": "A more complete metadata object that produces a more informative evaluation.",
                        "value": {
                            "tool_metadata": {
                                "name": "Flower",
                                "type": ["lib"],
                                "description": [
                                    "A framework for federated learning"
                                ],
                                "label": [
                                    "Flower"
                                ],
                                "repository": [
                                    "https://github.com/adap/flower"
                                ],
                                "webpage": [
                                    "https://flower.ai"
                                ],
                                "version": [
                                    "1.13.0"
                                ],
                                "version_control": True,
                                "license": [
                                    {
                                        "name": "Apache License 2.0",
                                        "url": "https://opensource.org/licenses/Apache-2.0"
                                    }
                                ],
                                "documentation": [
                                    {
                                        "type": "readme",
                                        "url": "https://github.com/adap/flower/blob/main/README.md"
                                    }
                                ],
                                "authors": [
                                    {
                                        "name": "Jane Doe",
                                        "type": "person",
                                        "email": "jane@example.org",
                                        "maintainer": True
                                    }
                                ],
                                "publication": [
                                    {
                                        "title": "Flower: A Friendly Federated Learning Research Framework",
                                        "year": 2023,
                                        "doi": "10.48550/arXiv.2007.14390"
                                    }
                                ],
                                "topics": [
                                    {
                                        "term": "machine learning",
                                        "vocabulary": "EDAM"
                                    }
                                ],
                                "input": [
                                    {
                                        "term": "CSV",
                                        "vocabulary": "EDAM"
                                    }
                                ],
                                "output": [
                                    {
                                        "term": "model",
                                        "vocabulary": "EDAM"
                                    }
                                ]
                            },
                            "prepare": False
                        },
                    },
                }
            ),
        ]
    ):
    try:
        tool_metadata = data.tool_metadata
        prepare = data.prepare
        
        # Check if preparation is needed
        if prepare:
            try:
                prepared_tool = prepareMetadataForEvaluation(tool_metadata)
            except Exception as e:
                logging.error(f"Error during metadata preparation: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Metadata preparation failed: {str(e)}")
        else:
            prepared_tool = tool_metadata
        
        # Create an instance object
        try:
            instance = Instance(**prepared_tool)
        except Exception as e:
            logging.error(f"Error creating instance: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Instance creation failed: {str(e)}")
        
        # Compute metrics
        try:
            computation = IndicatorComputation(instance)
            computation.compute_indicators()
        except Exception as e:
            logging.error(f"Error computing indicators: {str(e)}")
            tb_str = traceback.format_exc()  # Capture full traceback as string
            logging.error(f"Error computing indicators:\n{tb_str}")
            raise HTTPException(status_code=500, detail=f"Error computing indicators:\n{tb_str}")
        
        # Compute FAIR scores and get the result dictionary
        try:
            result = compute_fair_scores(instance)
            logs = instance.logs.__dict__
            feedback = get_feedback(result)

        except Exception as e:
            raise
            #logging.error(f"Error computing FAIR scores: {str(e)}")
            #raise HTTPException(status_code=500, detail=f"Error computing FAIR scores: {str(e)}")

        # If all goes well, prepare the response
        response_data = {
            'result': result,
            'logs': logs,
            'feedback': feedback
        }
        
        return JSONResponse(content=response_data)

    except HTTPException as http_exc:
        # Return the HTTP error response directly
        return JSONResponse(content={"error": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        # Catch any unexpected exceptions and return a generic error response
        logging.error(f"Unexpected error: {str(e)}")
        return JSONResponse(content={"error": "An unexpected error occurred."}, status_code=500)
    

@router.post('/evaluateId', tags=["fair"])
async def evaluateId(request: Request):
    data = await request.json()
    id_ = data.get('id')
    if id_:
        tool = tools_collection.find_one({'@id': id_})
        if tool:
            # Create an instance object
            instance = Instance(**tool)

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



