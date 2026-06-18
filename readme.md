🧠 CogniGraph AI

An Enterprise-Grade Agentic RAG Architecture

Synthesize complex academic papers instantly using parallel Vector & Graph Database retrieval, orchestrated by stateful AI Agents.

🚀 Overview

CogniGraph AI is a full-stack, production-ready implementation of Agentic Retrieval-Augmented Generation (RAG). Unlike basic RAG systems that rely on a single vector database, CogniGraph uses an LLM-powered router to intelligently distribute queries across a Qdrant Vector Database (for conceptual semantic search) and a Neo4j Graph Database (for explicit relational and entity traversal).

The entire system is orchestrated by a state machine built with LangGraph, wrapped in an asynchronous FastAPI backend, and served to a sleek, glassmorphic React/Tailwind frontend.

✨ Core Features

🧠 Agentic Routing: Uses Llama 3.3 (via Groq) to analyze user intent and dynamically route queries to the correct database (or both simultaneously via Fan-out/Fan-in execution).

🕸️ Hybrid Context: Combines chunked textual data (Dense Embeddings) with relationship mapping (Knowledge Graphs) to prevent LLM hallucinations on complex logic.

📄 Parent-Child Chunking: Advanced document ingestion that preserves the hierarchical context of academic PDFs.

🛡️ Strict Type Validation: Uses Pydantic to enforce rigid JSON data contracts between the LLM and the frontend UI.

⚡ Asynchronous Microservices: Fully async backend capable of handling high concurrency without blocking.

💎 Premium UI: A Vercel/Linear-inspired dark-mode interface featuring dynamic metrics, interactive file uploading, and structured data visualization.

🏗️ Architecture & Tech Stack

Backend

Framework: FastAPI (Python)

Orchestration: LangGraph & LangChain

LLM Engine: Groq API (Llama 3.3 70B)

Embedding Model: BAAI/bge-small-en-v1.5 (Local, via FastEmbed)

Vector Storage: Qdrant (Persistent Local / Cloud)

Graph Storage: Neo4j (Cypher)

Frontend

Framework: React + Vite

Styling: Tailwind CSS + Lucide Icons

Design: Glassmorphism, CSS Grid, Responsive Mobile-First

🛠️ Local Setup & Installation

1. Clone the Repository

git clone [https://github.com/yourusername/cognigraph-ai.git](https://github.com/yourusername/cognigraph-ai.git)
cd cognigraph-ai


2. Backend Environment Setup

Create a Python virtual environment and install the dependencies (Using uv or pip).

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt


3. Environment Variables

Create a .env file in the root directory and add the following keys:

# AI Models
GROQ_API_KEY=gsk_your_groq_key_here

# Graph Database (Neo4j Aura or Local Desktop)
NEO4J_URI=neo4j+s://your-db-id.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password


4. Populate Databases (Optional but Recommended)

To test the retrieval system locally, you need data in your databases.
Place a sample academic PDF in the root folder as sample_paper.pdf and run:

# Ingest PDF into Qdrant Vector DB
python -m core.populate

# Inject sample relational data into Neo4j
python -m core.populate_graph


🏃‍♂️ Running the Application

This architecture requires running the backend and frontend simultaneously.

Terminal 1: FastAPI Backend

# Start the API server on port 8000
uvicorn main:app --host 0.0.0.0 --port 8000


API Docs available at: http://localhost:8000/docs

Terminal 2: React Frontend

cd frontend
npm install
npm run dev


UI available at: http://localhost:5173

🗺️ Project Structure

cognigraph-ai/
├── api/
│   └── routes.py            # FastAPI endpoints (REST interface)
├── core/
│   ├── agents.py            # LangChain Groq routing/summarization logic
│   ├── graph.py             # LangGraph state machine & orchestration
│   ├── ingestion.py         # PDF parsing & parent-child chunking
│   ├── retrieval.py         # Qdrant & Neo4j parallel search engine
│   ├── populate.py          # Script: Upload vectors to Qdrant
│   └── populate_graph.py    # Script: Inject mock entities to Neo4j
├── database/
│   └── connections.py       # DB connection singletons & lifecycle hooks
├── frontend/
│   ├── src/App.jsx          # React UI components
│   └── tailwind.config.js   # UI theme configuration
├── main.py                  # Uvicorn entry point & CORS setup
├── requirements.txt         # Python dependencies
└── .env                     # Secrets (Git-ignored)


🌐 Deployment (Cloud)

CogniGraph AI is designed for decoupled, serverless deployment:

Databases: Hosted on Qdrant Cloud and Neo4j AuraDB.

Backend: Deployed via Render (Web Service).

Frontend: Deployed via Vercel.

(See deployment_guide.md for full step-by-step cloud integration)