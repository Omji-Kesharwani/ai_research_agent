import os
import logging
from typing import List, Dict, Any

from database.connections import vector_db, graph_db
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self):
        self.qdrant = vector_db.get_client()
        self.collection_name = vector_db.collection_name
        self.neo4j_driver = graph_db.driver
        
        try:
            # Initialize Google Gemini Embeddings
            logger.info("Initializing Gemini Embedding Model for Retrieval...")
            self.embedding_model = HuggingFaceInferenceAPIEmbeddings(
                api_key=os.getenv("HF_TOKEN"),
                model_name="BAAI/bge-small-en-v1.5"
            )
        except Exception as e:
            logger.error(f"Failed to load Gemini Embedding model: {str(e)}")
            raise e

    def _get_dense_embedding(self, text: str) -> List[float]:
            """Converts a text query into a 384-dimensional vector using HF API."""
            return self.embedding_model.embed_query(text)
            
    def vector_search(self, query: str, top_k: int = 3) -> List[str]:
        """Executes a Dense Search in Qdrant using the modern query_points API."""
        logger.info(f"Executing Vector DB search for query: '{query}'")
        try:
            query_vector = self._get_dense_embedding(query)
            
            response = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=top_k,
                with_payload=True 
            )
            
            # The results are now nested inside the '.points' attribute of the response
            chunks = [hit.payload.get("text", "") for hit in response.points if hit.payload]
            
            logger.info(f"Retrieved {len(chunks)} chunks from Qdrant.")
            return chunks
        except Exception as e:
            logger.error(f"Vector search execution failed: {str(e)}")
            return [] # Fail gracefully to keep the agent alive

    def graph_search(self, entity_keyword: str) -> List[str]:
        """Executes a Cypher query to pull neighborhood context."""
        if not self.neo4j_driver:
            logger.warning("Graph database inactive. Bypassing graph retrieval.")
            return []

        logger.info(f"Executing Graph DB traversal for entity: '{entity_keyword}'")
        cypher_query = """
        MATCH (n)-[r]->(m)
        WHERE toLower(n.name) CONTAINS toLower($keyword) 
           OR toLower(m.name) CONTAINS toLower($keyword)
        RETURN n.name + ' ' + type(r) + ' ' + m.name AS relationship
        LIMIT 5
        """
        
        relationships = []
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(cypher_query, keyword=entity_keyword)
                for record in result:
                    relationships.append(record["relationship"])
            logger.info(f"Retrieved {len(relationships)} graph relationships.")
            return relationships
        except Exception as e:
            logger.error(f"Graph traversal failed: {str(e)}")
            return []

    def retrieve_context(self, query: str, keyword: str) -> Dict[str, Any]:
        """Orchestrates parallel retrievals."""
        logger.info(f"Starting Context Retrieval Pipeline. Query: '{query}', Keyword: '{keyword}'")
        
        vector_results = self.vector_search(query)
        graph_results = self.graph_search(keyword)
        
        return {
            "vector_chunks": vector_results,
            "graph_relations": graph_results
        }

# --- Local Verification Test ---
if __name__ == "__main__":
    retriever = HybridRetriever()
    test_query = "How does the Transformer model improve accuracy?"
    test_keyword = "Transformer"
    
    results = retriever.retrieve_context(test_query, test_keyword)
    logger.info("Retrieval Verification Complete.")