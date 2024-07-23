from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.helpers.prepareVocabularies import prepareEDAM

import json

router = APIRouter()

@router.get('/EDAMTerms', tags=["spdx"])
async def EDAMTerms():
    try:
        EDAMVocabularyItems = prepareEDAM()
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the EDAM vocabulary :(")
    return JSONResponse(content=EDAMVocabularyItems)

@router.get('/SPDXLicenses',  tags=["spdx"])
async def SPDXLicenses():
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        SPDXLicenses = [license['name'] for license in data['licenses']]
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the SPDX licenses :(")
    return JSONResponse(content=SPDXLicenses)

@router.get('/SPDXLicenses/url/{license}', tags=["spdx"])
async def SPDXLicenseURL(license: str):
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        URL = ''
        for l in data['licenses']:
            if l['name'] == license:
                URL = l['reference']
                break
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the URL of the SPDX license :(")
    return JSONResponse(content={"URL": URL})

@router.get('/SPDXLicenses/match/{license}', tags=["spdx"])
async def SPDXLicenseMatch(license: str):
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        match = ''
        for l in data['licenses']:
            if l['name'] == license:
                match = l['licenseId']
                break
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the SPDX license :(")
    return JSONResponse(content={"match": match})

