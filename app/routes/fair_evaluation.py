from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.routes.fairsoft import run_fairsoft_evaluation
from app.helpers.database import connect_DB
from app.models.instance import Instance
from app.services.indicator_computation import IndicatorComputation
from app.services.fair_scores import compute_fair_scores
from pydantic import BaseModel,  Field
import logging
from app.services.fairsoft_evaluation import run_fairsoft_evaluation
from typing import Dict, Any, Optional




router = APIRouter()

tools_collection, stats, pubs_collection, availability_collection = connect_DB()

class MetadataRequest(BaseModel):
    tool_metadata: Dict[str, Any] = Field(
        ...,
        description="The metadata related to the tool that needs to be evaluated."
    )
    prepare: Optional[bool] = Field(
        True,
        description="Indicates whether the metadata needs to be prepared before evaluation. Defaults to True."
    )


@router.post("/evaluate", deprecated=True, include_in_schema=False)
async def evaluate_fair_legacy(
    request: Request,
    data: MetadataRequest
):
    try:
        response_data = await run_fairsoft_evaluation(
            tool_metadata=data.tool_metadata,
            prepare=data.prepare,
        )
        return JSONResponse(content=response_data)

    except HTTPException as http_exc:
        return JSONResponse(
            content={"error": http_exc.detail},
            status_code=http_exc.status_code,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content={"error": "An unexpected error occurred."},
            status_code=500,
        )
    


