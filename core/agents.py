
import os
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException

# 1. Configure Production Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class PaperSummary(BaseModel):
    """Strict JSON schema for the LLM to follow when summarizing papers."""
    core_hypotheses: List[str] = Field(description="The main arguments or hypotheses of the paper.")
    methodology: str = Field(description="A concise explanation of how the research was conducted.")
    key_findings: List[str] = Field(description="The final measurable results or conclusions.")
    data_gaps: Optional[str] = Field(default=None, description="Any limitations or missing data noted by the authors.")

class RoutingDecision(BaseModel):
    """Schema to determine which database the agent should query."""
    route_to_vector: bool = Field(description="True if the query asks for general concepts or methodology.")
    route_to_graph: bool = Field(description="True if the query asks about relationships between specific entities, models, or authors.")
    extracted_entity: Optional[str] = Field(default=None, description="The specific model or concept name to search in the graph.")


class ResearchAgentService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY is missing from environment variables.")
            raise ValueError("LLM API key is required to initialize agents.")
            
        # Initialize a fast, production-ready LLM (Llama 3 via Groq)
        logger.info("Initializing Research Agent Service...")
        self.llm = ChatGroq(
            api_key=api_key,
            model_name="llama-3.3-70b-versatile", 
            temperature=0.1, # Low temperature for analytical consistency
            max_retries=3    # Production resilience: retry if API drops
        )

    async def route_query(self, user_query: str) -> RoutingDecision:
        """
        Asynchronous agent that decides which database to ping based on the user's intent.
        Uses structured output to guarantee a valid Python object is returned.
        """
        logger.info(f"Routing query: {user_query}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI routing assistant. Analyze the user's academic query and determine the optimal database routing strategy."),
            ("human", "{query}")
        ])
        
        # Bind the Pydantic schema to force the LLM to output JSON matching our model
        structured_llm = self.llm.with_structured_output(RoutingDecision)
        chain = prompt | structured_llm
        
        try:
            # Note the 'ainvoke' for asynchronous execution
            decision: RoutingDecision = await chain.ainvoke({"query": user_query})
            logger.info(f"Routing decision successful: {decision.dict()}")
            return decision
        except Exception as e:
            logger.error(f"Routing agent failed: {str(e)}")
            # Fallback strategy: default to vector search if LLM fails
            return RoutingDecision(route_to_vector=True, route_to_graph=False, extracted_entity=None)

    async def summarize_chunk(self, text_chunk: str) -> Optional[PaperSummary]:
        """
        Asynchronously summarizes a dense academic chunk into strict JSON variables.
        """
        logger.info("Starting chunk summarization...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert academic researcher. Extract the requested fields from the following text chunk. If a field is not present in the text, leave it blank or None. Do not hallucinate."),
            ("human", "Text Chunk:\n{text}")
        ])
        
        structured_llm = self.llm.with_structured_output(PaperSummary)
        chain = prompt | structured_llm
        
        try:
            summary: PaperSummary = await chain.ainvoke({"text": text_chunk})
            logger.info("Summarization complete.")
            return summary
        except Exception as e:
            logger.error(f"Summarization agent failed: {str(e)}")
            return None

# --- Local Async Test ---
if __name__ == "__main__":
    import asyncio

    async def run_tests():
        agent_service = ResearchAgentService()
        
        # Test 1: The Router
        decision = await agent_service.route_query("How does Method X improve upon the Transformer architecture?")
        print("\n--- Router Output ---")
        print(decision.model_dump_json(indent=2))
        
        # Test 2: The Summarizer
        sample_text = "We propose a novel framework. Our experiments yielded a 15% increase in accuracy over baseline models. However, the system struggles with low-light image processing."
        summary = await agent_service.summarize_chunk(sample_text)
        print("\n--- Summarizer Output ---")
        if summary:
            print(summary.model_dump_json(indent=2))

    # Run the async loop
    asyncio.run(run_tests())