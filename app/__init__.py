from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stats, metadata, spdx_edam, fair_evaluation, search

app = FastAPI()

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
app.include_router(spdx_edam.router, prefix="/spdx")
app.include_router(fair_evaluation.router, prefix="/fair")
app.include_router(search.router, prefix="")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3500, log_level='debug')
