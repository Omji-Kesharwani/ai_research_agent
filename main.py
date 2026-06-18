
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Research Assistant Engine",
    description="Agentic RAG Backend powering document analysis and graph traversal.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
  
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")

logger.info("FastAPI Server initialized and routes mounted.")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)