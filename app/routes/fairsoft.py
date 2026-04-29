import logging
from pydantic import BaseModel,  Field
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB
from typing import Dict, Any, Optional, Annotated
from fastapi import APIRouter, HTTPException, Request, Body
from app.helpers.fairsoft_evaluation import fairsoft_evaluation


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


@router.post("/evaluate", tags=["fairsoft"])
async def evaluate_fairsoft(
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
                        "prepare": False,
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
        response_data = await fairsoft_evaluation(
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

