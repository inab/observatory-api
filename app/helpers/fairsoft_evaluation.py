
import logging
import traceback
from typing import Dict, Any
from app.helpers.utils import prepareMetadataForEvaluation
from fastapi import HTTPException
from fairsoft_core import run_fairsoft_evaluation


async def fairsoft_evaluation(
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
        result = run_fairsoft_evaluation(prepared_tool)
    except Exception as e:
        logging.error(f"Error evaluating tool metadata")
        raise HTTPException(
            status_code=400,
            detail=f"Error evaluating tool metadata: {str(e)}",
        )

    return result
