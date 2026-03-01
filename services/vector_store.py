import json
import re
import chromadb
from pydantic import BaseModel, Field
from typing import List, Literal
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import USE_GROQ, GROQ_API_KEY, LOCAL_LLM_MODEL

# ── Config ───────────────────────────────────────────────
CHROMA_PATH = "./chroma_db"
COLLECTION  = "grants"
MODEL_NAME  = "all-MiniLM-L6-v2"

# Singletons — load once, reuse across all requests
_embedding_model = None
_collection      = None

def _get_resources():
    global _embedding_model, _collection
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(MODEL_NAME)
        client      = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION)
    return _embedding_model, _collection


def clean_html(text: str) -> str:
    return re.sub(r'<[^>]+>', ' ', text or '').strip()

def proposal_to_text(proposal: dict) -> str:
    return f"""
    Title: {proposal.get('project_title', '')}
    Mission: {proposal.get('primary_mission', '')}
    Beneficiaries: {', '.join(proposal.get('target_beneficiaries', []))}
    Geography: {', '.join(proposal.get('geographic_focus', []))}
    Activities: {', '.join(proposal.get('key_activities', []))}
    SDGs: {', '.join(proposal.get('sdg_alignment', []))}
    Cause Area: {proposal.get('cause_area', '')}
    """.strip()

# --- 1. NEW PYDANTIC MODELS FOR STRICT RAG OUTPUT ---
class GrantMatchInsight(BaseModel):
    grant_id: str = Field(description="The exact ID of the grant being evaluated")
    match_explanation: str = Field(description="2-3 sentences explaining EXACTLY why this grant matches the proposal's mission or location.")
    fit_level: Literal["strong", "moderate", "weak"] = Field(description="How good of a fit is this grant?")
    application_tip: str = Field(description="One concrete, actionable tip to strengthen the application for this specific funder.")

class GrantMatchInsightsList(BaseModel):
    insights: List[GrantMatchInsight] = Field(description="A list containing exactly one insight for every retrieved grant provided in the prompt.")

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert grant advisor helping NGOs find the best funding matches.
You will be given an NGO proposal and a list of retrieved grants.
For every single grant in the 'Retrieved Grants' list, evaluate the fit, explain the match, and provide an application tip.
Do not skip any grants."""),
    ("user", """NGO Proposal:
{proposal}

Retrieved Grants:
{grants}""")
])

def get_llm(USE_GROQ):
    if USE_GROQ:
        return ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
    return ChatOllama(model=LOCAL_LLM_MODEL)

def find_similar_grants(proposal: dict, top_k: int = 5) -> list:
    model, collection = _get_resources()

    # Load full grant details
    with open("data/grants_enriched.json") as f:
        raw = json.load(f)
        grant_list = raw.get("grants", raw) if isinstance(raw, dict) else raw
        all_grants = {str(g["grant_id"]): g for g in grant_list}

    # Step 1 — Embed proposal and retrieve from ChromaDB
    proposal_embedding = model.encode(proposal_to_text(proposal)).tolist()

    results = collection.query(
        query_embeddings=[proposal_embedding],
        n_results=top_k,
        include=["metadatas", "distances"]
    )

    # Step 2 — Build retrieved grants context
    retrieved = []
    for grant_id, distance, metadata in zip(
        results["ids"][0],
        results["distances"][0],
        results["metadatas"][0]
    ):
        similarity_score = round((1 - distance) * 100, 1)
        full_grant = all_grants.get(grant_id, {})

        retrieved.append({
            "grant_id":        grant_id,
            "similarity_score": similarity_score,
            "title":           metadata.get("title", ""),
            "agency":          metadata.get("agency", ""),
            "award_floor":     metadata.get("award_floor", 0),
            "award_ceiling":   metadata.get("award_ceiling", 0),
            "application_url": metadata.get("application_url", ""),
            "close_date":      metadata.get("close_date", ""),
            "focus_areas":     metadata.get("focus_areas", ""),
            "contact_email":   metadata.get("contact_email", ""),
            "description":     clean_html(full_grant.get("description", "")),
            "eligibility":     full_grant.get("eligibility", []),
        })

    # Step 3 — RAG: Local LLM with Pydantic Strict Typing
    print(f"🧠 Generating RAG explanations using {'Groq' if USE_GROQ else 'Local Ollama'}...")
    # print(f"🧠 Generating RAG explanations...")
    llm = get_llm(USE_GROQ)
    structured_llm = llm.with_structured_output(GrantMatchInsightsList)
    chain = RAG_PROMPT | structured_llm

    try:
        # CONTEXT SAVER: Only send the LLM the fields it actually needs to reason about the match
        slim_retrieved = [
            {
                "grant_id": g["grant_id"], 
                "title": g["title"], 
                "agency": g["agency"], 
                "description": g["description"][:1000] # Cap description length
            } for g in retrieved
        ]
        
        result = chain.invoke({
            "proposal": json.dumps(proposal, indent=2),
            "grants": json.dumps(slim_retrieved, indent=2)
        })
        
        # Map Pydantic objects back to a dictionary using grant_id as the key
        rag_insights = {str(insight.grant_id): insight for insight in result.insights}
        
    except Exception as e:
        print(f"⚠️ RAG LLM Error: {e}")
        rag_insights = {}

    # Step 4 — Merge vector results with RAG insights
    final = []
    for grant in retrieved:
        insight = rag_insights.get(str(grant["grant_id"]))
        
        final.append({
            **grant,
            "match_explanation": insight.match_explanation if insight else "Local model reasoning unavailable.",
            "fit_level":         insight.fit_level if insight else "unknown",
            "application_tip":   insight.application_tip if insight else "Review funder guidelines carefully.",
        })

    return sorted(final, key=lambda x: x["similarity_score"], reverse=True)