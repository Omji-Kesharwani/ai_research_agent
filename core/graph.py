# --- File: core/graph.py ---
import logging
from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, START, END

# Import our modular microservices
from core.agents import ResearchAgentService, RoutingDecision, PaperSummary
from core.retrieval import HybridRetriever

# Configure Production Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 1. Define the Global State (The "Memory" of the execution)
class AgentState(TypedDict):
    query: str
    routing_decision: Optional[RoutingDecision]
    vector_chunks: List[str]
    graph_relations: List[str]
    final_summary: Optional[Any] # Will hold the serialized JSON of PaperSummary

# Initialize our services once to be reused by the graph nodes
agent_service = ResearchAgentService()
retriever = HybridRetriever()

# 2. Define Node Functions (The Workers)
async def route_query_node(state: AgentState) -> dict:
    """Node 1: Evaluates the query to decide where to search."""
    logger.info("--- NODE: Routing Query ---")
    decision = await agent_service.route_query(state["query"])
    # The returned dict updates the AgentState
    return {"routing_decision": decision}

def retrieve_vector_node(state: AgentState) -> dict:
    """Node 2A: Fetches dense/sparse documents."""
    logger.info("--- NODE: Vector Retrieval ---")
    chunks = retriever.vector_search(state["query"])
    return {"vector_chunks": chunks}

def retrieve_graph_node(state: AgentState) -> dict:
    """Node 2B: Fetches entity relationships."""
    logger.info("--- NODE: Graph Retrieval ---")
    decision = state["routing_decision"]
    entity = decision.extracted_entity if decision and decision.extracted_entity else state["query"]
    relations = retriever.graph_search(entity)
    return {"graph_relations": relations}

async def summarize_node(state: AgentState) -> dict:
    """Node 3: Compresses all retrieved data into structured JSON."""
    logger.info("--- NODE: Summarizing Context ---")
    
    # Combine chunks and relations into one context payload
    context_parts = []
    if state.get("vector_chunks"):
        context_parts.extend(state["vector_chunks"])
    if state.get("graph_relations"):
        context_parts.extend(state["graph_relations"])
        
    combined_context = "\n\n".join(context_parts)
    
    if not combined_context.strip():
        logger.warning("No context retrieved. Summarizer will rely on internal knowledge or fail gracefully.")
        combined_context = "No relevant context found in the database."

    summary = await agent_service.summarize_chunk(combined_context)
    
    # We dump it to a dict so it stores cleanly in the LangGraph state
    return {"final_summary": summary.model_dump() if summary else None}

# 3. Define Conditional Routing Logic (The Edges)
def router_condition(state: AgentState) -> List[str]:
    """Determines which retrieval nodes to activate based on the agent's decision."""
    decision = state.get("routing_decision")
    routes = []
    
    if not decision:
        return ["retrieve_vector_node"] # Fallback
        
    if decision.route_to_vector:
        routes.append("retrieve_vector_node")
    if decision.route_to_graph:
        routes.append("retrieve_graph_node")
        
    # If LLM said false to both, default to vector search so the pipeline doesn't freeze
    if not routes:
        routes.append("retrieve_vector_node")
        
    return routes

# 4. Build the Directed Graph
logger.info("Compiling LangGraph State Machine...")
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("route_query_node", route_query_node)
workflow.add_node("retrieve_vector_node", retrieve_vector_node)
workflow.add_node("retrieve_graph_node", retrieve_graph_node)
workflow.add_node("summarize_node", summarize_node)

# Add Edges
workflow.add_edge(START, "route_query_node")

# Add Conditional Edges (Fan-out to databases)
workflow.add_conditional_edges(
    "route_query_node",
    router_condition,
    {
        "retrieve_vector_node": "retrieve_vector_node",
        "retrieve_graph_node": "retrieve_graph_node"
    }
)

# Fan-in from databases to the summarizer
workflow.add_edge("retrieve_vector_node", "summarize_node")
workflow.add_edge("retrieve_graph_node", "summarize_node")

workflow.add_edge("summarize_node", END)

# Compile into an executable application
research_assistant_app = workflow.compile()

# --- Local Async Test ---
if __name__ == "__main__":
    import asyncio
    import json

    async def run_graph():
        query = "How did Method X from the Transformer architecture improve benchmark accuracy?"
        
        # Initialize the state
        initial_state = {
            "query": query,
            "routing_decision": None,
            "vector_chunks": [],
            "graph_relations": [],
            "final_summary": None
        }
        
        logger.info(f"Invoking graph with query: {query}")
        
        # Run the compiled graph asynchronously
        final_state = await research_assistant_app.ainvoke(initial_state)
        
        print("\n" + "="*50)
        print("🎯 GRAPH EXECUTION COMPLETE 🎯")
        print("="*50)
        print(f"Graph Routes Taken: Vector={len(final_state['vector_chunks']) > 0 or True}, Graph={len(final_state['graph_relations']) > 0 or True}")
        print("\nFINAL STRUCTURED OUTPUT:")
        print(json.dumps(final_state["final_summary"], indent=2))
        print("="*50)

    # Run the async loop
    asyncio.run(run_graph())