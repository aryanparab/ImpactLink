import json
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Import central config
from config import USE_GROQ, GROQ_API_KEY, LOCAL_LLM_MODEL

# 1. Structured Schema for Funder Matching
class FunderMatch(BaseModel):
    funder_id: str = Field(description="The unique ID of the funder")
    fit_score: int = Field(description="Score 0-100 based on alignment", ge=0, le=100)
    match_reason: str = Field(description="1-2 sentences explaining the match")
    gaps: str = Field(description="What is missing or misaligned")
    recommendation: str = Field(description="One specific adjustment to improve fit")

class FunderMatchList(BaseModel):
    matches: List[FunderMatch]

# 2. Dynamic Resource Loading
def get_matching_llm():
    if USE_GROQ:
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=GROQ_API_KEY)
    return ChatOllama(model=LOCAL_LLM_MODEL, temperature=0, format="json")

# 3. Matching Prompt
MATCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a grant matching expert. Given an NGO proposal and a list of funders,
score each funder's fit with the proposal.

For each funder return:
- funder_id: string
- fit_score: number 0-100
- match_reason: string (1-2 sentences explaining why they match)
- gaps: string (1 sentence on what's missing or misaligned)
- recommendation: string (one specific thing to adjust in the proposal to improve fit)

Return ONLY a JSON array of funder match objects, nothing else."""),
    ("human", """Proposal:
{proposal_json}

Available Funders:
{funders_json}

Return ranked matches from highest to lowest fit score.""")
])

def find_similar_grants(proposal: dict, top_k: int = 5) -> list:
    # Load funder database
    funders_path = os.path.join(os.path.dirname(__file__), "../data/funders.json")
    with open(funders_path, "r") as f:
        funders_db = json.load(f)

    llm = get_matching_llm()
    structured_llm = llm.with_structured_output(FunderMatchList)
    chain = MATCH_PROMPT | structured_llm

    try:
        mode_name = "Groq" if USE_GROQ else "Local Ollama"
        print(f"🔍 Finding matches via {mode_name}...")

        # Invoke chain
        result = chain.invoke({
            "proposal_json": json.dumps(proposal, indent=2),
            "funders_json": json.dumps(funders_db, indent=2)
        })

        # Step 2: Enrich and Sort
        funder_map = {f["id"]: f for f in funders_db}
        final_matches = []
        
        # Sort by fit_score descending
        sorted_results = sorted(result.matches, key=lambda x: x.fit_score, reverse=True)

        for match in sorted_results[:top_k]:
            detail = funder_map.get(match.funder_id, {})
            final_matches.append({
                **detail,
                **match.model_dump()
            })

        return final_matches

    except Exception as e:
        print(f"❌ Matching Error: {e}")
        return []