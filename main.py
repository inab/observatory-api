from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.routes import edam, spdx, stats, metadata, fair_evaluation, search, tool

tags_metadata = [
        {
            "name": "stats",
            "description": "Stats related endpoints",
        }, 
        {
            "name": "tools",
            "description": "Tools related endpoints",
        },
        {
            "name": "vocabularies",
            "description": "SPDX and EDAM related endpoints",
        },
        {
            "name": "fair",
            "description": "FAIR Evaluation related endpoints",
        },
        {
            "name": "search",
            "description": "Search related endpoints",
        },
    ]

app = FastAPI(
    title="Software Observatory API",
    description="This is the API for the Software Observatory at [OpenEBench](https://openebench.bsc.es)",
    version="2.0.0",
    contact={
        "name": "OpenEBench",
        "url": "https://openebench.bsc.es/",
    },
    openapi_tags=tags_metadata
    
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(stats.router, prefix="/stats")
app.include_router(metadata.router, prefix="/tools")
app.include_router(edam.router, prefix="/edam")
app.include_router(spdx.router, prefix="/spdx")

app.include_router(fair_evaluation.router, prefix="/fair")
app.include_router(tool.router, prefix="/tool")
app.include_router(search.router, prefix="")



@app.get("/app")
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

@app.get("/docs", include_in_schema=False)
async def swagger_ui_html(req: Request) -> HTMLResponse:
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3500, log_level='debug')
