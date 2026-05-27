from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from app.helpers.database import connect_DB, connect_similarity_DB
from app.helpers.utils import prepare_sources_labels

router = APIRouter()

tools_collection, _stats, _pubs, _availability = connect_DB()
similarity_collection = connect_similarity_DB()


def _serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    return value


def _longest_description(descriptions):
    if not descriptions:
        return None
    return max(descriptions, key=len)


def _enrich_similar(similar_list):
    enriched = []
    for item in similar_list:
        entry = dict(item)
        try:
            tool_doc = tools_collection.find_one(
                {'_id': ObjectId(item['tool_id'])},
                projection={
                    'data.description': 1,
                    'data.name': 1,
                    'data.source': 1,
                    'data.repository': 1,
                    'data.links': 1,
                }
            )
            if tool_doc:
                data = tool_doc.get('data', {})
                entry['description'] = _longest_description(data.get('description', []))
                try:
                    prepare_sources_labels(data)
                    entry['sources_labels'] = data.get('sources_labels', {})
                except Exception:
                    entry['sources_labels'] = {}
            else:
                entry['description'] = None
                entry['sources_labels'] = {}
        except Exception:
            entry['description'] = None
            entry['sources_labels'] = {}
        enriched.append(entry)
    return enriched


@router.get('', tags=["similarity"])
async def get_similar_software(tool_id: str):
    try:
        doc = similarity_collection.find_one({'tool_id': tool_id})
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Error fetching similar software: {err}")

    if doc is None:
        raise HTTPException(status_code=404, detail=f"No similarity data found for tool_id: {tool_id}")

    doc['id'] = str(doc.pop('_id'))
    doc['similar'] = _enrich_similar(doc.get('similar', []))
    return JSONResponse(content=_serialize(doc))
