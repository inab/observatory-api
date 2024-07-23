from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.helpers.prepareVocabularies import prepareEDAM

import json

router = APIRouter()

@router.get('/EDAMTerms', tags=["edam"])
async def EDAMTerms():
    try:
        EDAMVocabularyItems = prepareEDAM()
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the EDAM vocabulary :(")
    return JSONResponse(content=EDAMVocabularyItems)

