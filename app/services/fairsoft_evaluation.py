
import logging
import traceback
from typing import Dict, Any
from app.helpers.utils import prepareMetadataForEvaluation
from app.models.instance import Instance
from fastapi import APIRouter, HTTPException, Request, Body
from app.services.indicator_computation import IndicatorComputation 
from app.services.fair_scores import compute_fair_scores
from app.helpers.indicators_feedback import get_feedback 


async def run_fairsoft_evaluation(
    tool_metadata: dict,
    prepare: bool,
) -> dict[str, Any]:
    """
    Run FAIRsoft evaluation and return the response payload as a plain dict.

    Raises:
        HTTPException: for expected client/server errors.
    """
    # Prepare metadata if requested
    if prepare:
        try:
            prepared_tool = prepareMetadataForEvaluation(tool_metadata)
        except Exception as e:
            logging.error(f"Error during metadata preparation: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Metadata preparation failed: {str(e)}",
            )
    else:
        prepared_tool = tool_metadata

    # Build instance
    try:
        instance = Instance(**prepared_tool)
    except Exception as e:
        logging.error(f"Error creating instance: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Instance creation failed: {str(e)}",
        )

    # Compute indicators
    try:
        computation = IndicatorComputation(instance)
        computation.compute_indicators()
    except Exception as e:
        logging.error(f"Error computing indicators: {str(e)}")
        tb_str = traceback.format_exc()
        logging.error(f"Error computing indicators:\n{tb_str}")
        raise HTTPException(
            status_code=500,
            detail=f"Error computing indicators:\n{tb_str}",
        )

    # Compute FAIR scores and feedback
    try:
        result = compute_fair_scores(instance)
        logs = instance.logs.__dict__
        feedback = get_feedback(result)
    except Exception as e:
        logging.error(f"Error computing FAIR scores: {str(e)}")
        tb_str = traceback.format_exc()
        logging.error(f"Error computing FAIR scores:\n{tb_str}")
        raise HTTPException(
            status_code=500,
            detail=f"Error computing FAIR scores: {str(e)}",
        )

    return {
        "result": result,
        "logs": logs,
        "feedback": feedback,
    }
