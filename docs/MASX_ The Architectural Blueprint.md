# MASX: The Architectural Blueprint for an Autonomous Strategic Forecasting and Doctrine Synthesis Engine
The MASX engine is designed to be the world's most advanced strategic forecasting system. It achieves this by synthesizing high-velocity "world as events" data through a multi-agent "Council of Doctrines." This architecture enables the system to generate probabilistic, research-grade forecasts grounded in thousands of years of strategic wisdom and modern hybrid warfare principles.
## 1. Core Architecture: LlamaIndex-Powered Agentic RAG
The system is implemented as a stateful, directed acyclic graph (DAG) using LangGraph for orchestration, with LlamaIndex serving as the foundational data framework for Retrieval-Augmented Generation (RAG). This approach ensures that 23 unique doctrine agents have precise, high-fidelity access to their specific strategic corpora.
### The Forecasting Workflow (The "Reasoning Loop")
Intake Node: Continuously monitors the GDELT Event Database (georeferenced CAMEO events every 15 minutes) and Multilingual News RSS.1
ForecasterAgent: Decomposes the primary inquiry into "Decisive Strategic Questions." It enforces an "Outside View" (identifying reference class base rates) before proceeding.2
LlamaIndex SearchAgent: Performs agentic retrieval across the Global Knowledge Graph (GKG) and news vectors. It uses LlamaIndex's RouterQueryEngine to decide whether to perform a semantic search or a summarized overview of recent trends.
Doctrine Router: Analyzes the query and evidence to select the top 3–5 most relevant doctrine agents.
Doctrine Council (Parallel Processing): The selected agents operate as LlamaIndex Document Agents. Each agent is equipped with specific QueryEngineTools mapped to its unique RAG index (e.g., the *Art of War* index). This allows the agent to "query" its own doctrine for relevant heuristics and principles.
Synthesis Node (Master LLM): Resolves contradictions between doctrines and outputs a structured probabilistic forecast.
## 2. Phase 1: High-Fidelity PDF Ingestion & Ingestion Pipeline
To ensure "Deep Research" grade transparency, raw PDF doctrines are ingested using LlamaIndex's specialized parsing tools.
LlamaParse Integration: Raw PDFs for all 23 doctrines are processed via LlamaParse to ensure layout-aware parsing of complex tables and historical structures.
Vector Indexing: Parsed content is converted into document chunks and indexed using LlamaIndex VectorStoreIndex.
Narrative Gravity (GKG): Narrative signals—themes, emotions, and mentions—are ingested from GDELT to identify shifts in global sentiment before events occur.
Provenance Maintenance: LlamaIndex's metadata management ensures every retrieved chunk is linked back to its source PDF part and page number for auditability.
## 3. Phase 2: 23 Unique Doctrine Agents as Query Tools
The heart of the system is the deployment of 23 distinct agents, each acting as a specialized AI Query Tool powered by a LlamaIndex RAG pipeline.
## 4. Phase 3: Probabilistic Forecasting & Evaluation
MASX enforces scientific "sharpness" through structured output validation and scoring.
### Forecast Schema (Pydantic via LlamaIndex)
LlamaIndex's Structured Output module ensures every forecast is validated against a Pydantic schema:

Python

class Forecast(BaseModel):
    event_definition: str
    time_window: str
    probability: float = Field(ge=0, le=1)  # 0.0 to 1.0
    confidence_interval: List[float]
    drivers: List[str]
    disconfirming_evidence: List[str]
    signposts: List[str]  # Triggers for probability updates

### The Evaluation Harness: Brier Score Decomposition
The system logs every prediction and its outcome. It decomposes the Brier Score (BS) into Reliability (calibration), Resolution (sharpness), and Uncertainty (climatological base rate) to identify model failures.4
## 5. Phase 4: Scenario Cockpit & Shell Methodology
MASX utilizes Shell methodology to construct 3–5 plausible futures.5
Scenario Generation: Doctrine agents generate narratives based on "Critical Uncertainties" (e.g., *Archipelagos* vs. *Surge*).7
Signpost Monitoring: The "Scenario Cockpit" uses LlamaIndex SummaryIndex and VectorStoreIndex to track world events as indicators that suggest the world is drifting toward one specific future.
## 6. Implementation Roadmap: v1 to v2
### Engine v1 (Foundational MVP)
Deploy LlamaIndex with SimpleDirectoryReader for initial raw PDF ingestion.
Create 23 individual Vector Indexes, one for each doctrine part.
Expose these as QueryEngineTools to a FunctionAgent workflow.
### Engine v2 (Research-Grade)
Agentic Retrieval: Transition to LlamaCloudIndex for enterprise-grade managed retrieval and superior context management.
Reflection Loops: Use LlamaIndex Workflows to implement reflection on structured outputs, ensuring Brier probabilities are consistent and logical.
Cognitive Circuit Breakers: Implement retry budgets and loop detection to prevent agentic "hallucination loops".
## 7. Technical Stack

This blueprint transforms MASX into a "scientifically sharp" system, leveraging LlamaIndex's agentic RAG capabilities to provide the world's most robust window into geopolitical uncertainty.
#### Works cited
The GDELT Project, accessed February 16, 2026, 
Superforecasting LLM: Advanced Forecasting - Emergent Mind, accessed February 16, 2026, 
Evidence on good forecasting practices from the Good Judgment Project: an accompanying blog post - AI Impacts, accessed February 16, 2026, 
Brier score - Wikipedia, accessed February 16, 2026, 
Scenarios: An Explorer's Guide - Shell, accessed February 16, 2026, 
Explained: Shell's Scenarios for Data Centre Energy Futures, accessed February 16, 2026, 
Shell's Energy Scenarios: Turning Data into Insights - ortec, accessed February 16, 2026, 
Building Multi-Agent Systems with LangGraph: A Step-by-Step Guide | by Sushmita Nandi, accessed February 16, 2026, 
Data: Querying, Analyzing and Downloading - The GDELT Project, accessed February 16, 2026, 

| Category | Doctrine Agents | LlamaIndex Query Tool Implementation |
| --- | --- | --- |
| Classical Statecraft | Chanakya, Sun Tzu, Mahabharata, Panchatantra | QueryEngineTool focused on Saptanga (7-limb) indicators and Upayas (diplomatic methods). |
| Global Geopolitics | Heartland (Mackinder), Rimland (Spykman), Sea Power, Containment | Tools specialized in maritime choke points, pivot area control, and geographic barriers. |
| Power Realism | Diplomacy (Kissinger), Great Power Politics, RAND, Smart Power | RetrieverRouterQueryEngine for multi-stage analysis of power-maximizing revisionism and triangular diplomacy. |
| Hybrid & Cognitive | 5GW, Unrestricted Warfare, MindWar, LikeWar, Wag the Dog | Tools designed to scan for non-kinetic signals like "narrative battlefields" and perception management. |
| Governance & Ethics | Iroquois Great Law, Shivaji (Ganimi Kava), National Security Strategy | Tools focused on consensus models, "7th Generation" principles, and asymmetric fort-centric defense. |

| Component | Technology | Purpose |
| --- | --- | --- |
| Reasoning | Gemini 2.0 Flash / GPT-4o | High-speed, high-context reasoning.8 |
| Orchestration | LangGraph | Stateful multi-agent graph with checkpointing. |
| Data Framework | LlamaIndex | RAG orchestration, document parsing, and query tool abstraction. |
| Parsing | LlamaParse | High-accuracy layout parsing of raw doctrine PDFs. |
| Ingestion | Google BigQuery / GDELT | Real-time "World as Events" stream.1 |
| Evaluation | Pydantic Evals / Logfire | Brier score tracking and calibration. |
