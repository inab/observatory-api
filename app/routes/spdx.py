from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

@router.get('/SPDXLicenses',  tags=["spdx"])
async def SPDXLicenses():
    try:
        print(os.getcwd())
        with open('./app/routes/licenses.json') as f:
            data = json.load(f)
        SPDXLicenses = [license['licenseId'] for license in data['licenses']]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the SPDX licenses :(")
    return JSONResponse(content=SPDXLicenses)

@router.get('/SPDXLicenses/url/{license}', tags=["spdx"])
async def SPDXLicenseURL(license: str):
    try:
        with open('./app/routes/licenses.json') as f:
            data = json.load(f)
        URL = ''
        for l in data['licenses']:
            if l['licenseId'] == license:
                URL = l['reference']
                break
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the URL of the SPDX license :(")
    return JSONResponse(content={"URL": URL})

@router.get('/SPDXLicenses/match/{license}', tags=["spdx"])
async def SPDXLicenseMatch(license: str):
    try:
        with open('./app/routes/licenses.json') as f:
            data = json.load(f)
        match = ''
        for l in data['licenses']:
            if l['name'] == license:
                match = l['licenseId']
                break
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when retrieving the SPDX license :(")
    return JSONResponse(content={"match": match})

