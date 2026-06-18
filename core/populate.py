import os
import uuid
import logging
from langchain_upstage import UpstageEmbeddings
from qdrant_client.models import PointStruct

# Import your existing modules
from core.ingestion import DocumentIngestionService
from database.connections import vector_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

def populate_vector_db(pdf_path: str):
    """Reads a PDF, generates dense embeddings, and uploads them to Qdrant."""
    if not os.path.exists(pdf_path):
        logger.error(f"❌ File not found: {pdf_path}")
        logger.info("Please place a valid PDF in the project folder and update the path.")
        return

    # 1. Parse and Chunk the PDF (Reusing Phase 2)
    logger.info(f"📄 Processing PDF: {pdf_path}")
    ingestion_service = DocumentIngestionService()
    data = ingestion_service.process_pdf(pdf_path)
    child_chunks = data["children"]

    if not child_chunks:
        logger.warning("No text could be extracted from the PDF.")
        return

    # 2. Initialize the Embedding Model (Using Gemini API)
    logger.info("🧠 Loading Google Gemini Embedding model...")
    logger.info("🧠 Loading Upstage Cloud Embedding model...")
    embedding_model = UpstageEmbeddings(
        api_key=os.getenv("UPSTAGE_API_KEY"),
        model="solar-embedding-1-large"
    )
    # 3. Generate Embeddings for all child chunks
    logger.info(f"🔢 Generating vector embeddings for {len(child_chunks)} text chunks. This may take a moment...")
    texts_to_embed = [chunk.page_content for chunk in child_chunks]
    
    # Process in batches to respect API limits
    batch_size = 100
    embeddings = []
    for i in range(0, len(texts_to_embed), batch_size):
        batch_texts = texts_to_embed[i:i + batch_size]
        batch_embeddings = embedding_model.embed_documents(batch_texts)
        embeddings.extend(batch_embeddings)

    # 4. Format the payload for Qdrant
    points = []
    for chunk, embedding in zip(child_chunks, embeddings):
        point_id = str(uuid.uuid4())
        
        points.append(
            PointStruct(
                id=point_id,
                # We specifically target the "dense" named vector we set up in Phase 3
                vector={"dense": embedding}, 
                # We attach the text and relational metadata as the payload
                payload={
                    "text": chunk.page_content,
                    "parent_id": chunk.metadata.get("parent_id", ""),
                    "source": pdf_path,
                    "page": chunk.metadata.get("page", 0)
                }
            )
        )

    # 5. Upload to local persistent Qdrant storage
    logger.info("💾 Uploading data to Qdrant Cloud persistent storage...")
    client = vector_db.get_client()
    
    client.upsert(
        collection_name=vector_db.collection_name,
        points=points
    )
    
    logger.info("✅ Database population complete! Your agent now has memory.")

if __name__ == "__main__":
    # Make sure you have a sample paper in your root directory!
    target_pdf = "sample_paper.pdf" 
    populate_vector_db(target_pdf)