# --- File: database/connections.py ---
import os
import logging
import atexit  # PRODUCTION ADDITION: For clean shutdown management
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams
from neo4j import GraphDatabase

# Configure Production Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

class VectorDBManager:
    def __init__(self, collection_name: str = "academic_papers"):
        self.collection_name = collection_name
        
        
        logger.info(f"Initializing Qdrant client with persistent storage at: {self.storage_path}")
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self._initialize_collection()

    def _initialize_collection(self):
        """Creates a Qdrant collection configured for Hybrid Search if it doesn't exist."""
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Creating Hybrid Qdrant Collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={"dense": VectorParams(size=384, distance=Distance.COSINE)},
                    sparse_vectors_config={"sparse": SparseVectorParams()}
                )
            else:
                logger.info(f"Persistent collection '{self.collection_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {str(e)}")
            raise e
            
    def get_client(self) -> QdrantClient:
        return self.client

    def close(self):
        """Explicitly closes the local storage client reference cleanly."""
        if hasattr(self, 'client') and self.client is not None:
            try:
                # Call close explicitly before interpreter teardown
                self.client.close()
                logger.info("Qdrant persistent client connection closed cleanly.")
            except Exception as e:
                # Catch failures silently if the interpreter has already cleared components
                pass


class GraphDBManager:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, user, password]):
            logger.warning("Neo4j credentials missing from environment variables. Graph features will be bypassed.")
            self.driver = None
        else:
            self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=1800)

    def verify_connection(self) -> bool:
        if not self.driver:
            return False
        try:
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j Graph Database Cluster.")
            return True
        except Exception as e:
            logger.error(f"Failed to verify Neo4j connectivity: {str(e)}")
            return False

    def close(self):
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j active connection driver closed cleanly.")
            except Exception as e:
                pass

# --- Singleton Instances for Global App State ---
vector_db = VectorDBManager()
graph_db = GraphDBManager()

# --- Production Lifecycle Shutdown Registration ---
def cleanup_database_connections():
    """
    Executed automatically when the Python application terminates.
    Ensures explicit, graceful closure of persistent storage locks.
    """
    logger.info("Application lifecycle termination triggered. Cleaning up resources...")
    vector_db.close()
    graph_db.close()

# Register the cleanup hook with the runtime
atexit.register(cleanup_database_connections)

if __name__ == "__main__":
    logger.info("Running Database Layer sanity checks...")
    client = vector_db.get_client()
    logger.info(f"Available Collections: {client.get_collections()}")
    graph_db.verify_connection()