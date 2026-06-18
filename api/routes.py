import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from pydantic import BaseModel
from typing import List, Optional, Any
import os
# Import our compiled LangGraph state machine
from core.graph import research_assistant_app
from core.populate import populate_vector_db

logger = logging.getLogger(__name__)

# Create an APIRouter instance
router = APIRouter()

# 1. Define Request/Response Schemas (Data Contracts)
class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    summary: Optional[Any]
    vector_sources_count: int
    graph_relations_count: int

# 2. Define the Endpoint

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Receives a PDF from the frontend and populates the database."""
    logger.info(f"API received file upload: {file.filename}")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_location = f"./{file.filename}"
    
    try:
        # 1. Save file to disk
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Trigger the ingestion and embedding process
        populate_vector_db(file_location)
        
        # 3. Clean up the local PDF file after processing
        os.remove(file_location)
        
        return {"message": "Document successfully ingested", "filename": file.filename}
    except Exception as e:
        logger.error(f"Failed to process uploaded file: {str(e)}")
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """
    Receives a query, executes the LangGraph Agentic pipeline, 
    and returns the structured summary and citation counts.
    """
    logger.info(f"API received research query: '{request.query}'")
    
    # Initialize the required state for LangGraph
    initial_state = {
        "query": request.query,
        "routing_decision": None,
        "vector_chunks": [],
        "graph_relations": [],
        "final_summary": None
    }
    
    try:
        # Execute the graph asynchronously
        final_state = await research_assistant_app.ainvoke(initial_state)
        
        # Package the state into a clean HTTP response
        return ResearchResponse(
            query=final_state["query"],
            summary=final_state["final_summary"],
            vector_sources_count=len(final_state.get("vector_chunks", [])),
            graph_relations_count=len(final_state.get("graph_relations", []))
        )
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        # Return a clean 500 error to the frontend instead of crashing
        raise HTTPException(status_code=500, detail="Internal AI Processing Error")

@router.get("/health")
async def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "healthy", "service": "Agentic RAG Engine"}